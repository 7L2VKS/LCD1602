# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025,2026 7L2VKS

from smbus2 import SMBus
import time
from enum import Enum, auto

cmd = {'clear':0x01, 'home':0x02, 'entry':0x04, 'display':0x08, 'cursor':0x10, 'function':0x20, 'cgram':0x40, 'ddram':0x80}
rs  = {'cmd':0x00, 'data':0x01}
K   = 0x08

LCD_ROWS = 2
LCD_COLS = 16
DDRAM_ADDR_0 = 0x00
DDRAM_ADDR_1 = 0x40
BUFF_SIZE = 40
CUSTOM_FONT_HEIGHT = 8

class LCDAlignment(Enum):
    LEFT   = auto()
    CENTER = auto()
    RIGHT  = auto()

class LCD1602:
    '''
    A high-level controller class for operating an LCD1602 character display device over
    an I2C interface.

    This class provides a set of methods for controlling an LCD1602 device, including
    cursor movement, text displaying, buffer manipulation, text alignment handling, display
    configuration, and CGRAM pattern registration.

    The LCD1602 display consists of 2 rows x 16 columns, backed by a 40-character buffer
    per row. The class internally tracks the cursor position, buffer shift amount allowing
    the user to query cursor and buffer positions at any time.

    Custom characters may be registered in CGRAM using character codes in the range 0x00-0x07,
    each defined by an 8-row pattern.

    Parameters
    ----------
    i2c_address : int
        The I2C address of the LCD1602 device.
    cursor : bool, optional
        Whether the cursor is initially enabled. Default is True.
    blink : bool, optional
        Whether the cursor blinking mode is initially enabled. Default is False.
    backlight : bool, optional
        Whether the backlight is initially turned on. Default is True.

    Features
    --------
    - Write text at the cursor or at arbitrary display/buffer positions
    - Alignment-based text rendering (left, center, right)
    - Clear regions, rows, or the entire buffer
    - Move or shift the cursor and buffer
    - Enable or disable the display, cursor, blinking, and backlight
    - Register and clear custom characters in CGRAM (0x00-0x07)
    - Query cursor position (display or buffer) and buffer shift state
    '''

    def __init__(self, i2c_address:int, cursor:bool=True, blink:bool=False, backlight:bool=True) -> None:
        self.bus = SMBus(1)
        self.i2c_address = i2c_address
        self.backlight = backlight

        self.write_byte(0x33, rs['cmd'], wait_upper = 0.005)    # Initialize Sequence (4bit mode)
        self.write_byte(0x32, rs['cmd'])                        #    0b0011 0b0011 0b0011 0b0010
        self.write_byte(cmd['function'] | 0x0C, rs['cmd'])      # 2 rows, 5x11 font size
        self.clear_all()                                        # clear all, initialize shift and cursor position
        self.command_display(True, cursor, blink)               # set display(on), cursor, blink state
        self.write_byte(cmd['entry'] | 0x02, rs['cmd'])         # cursor right, data shift off

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False

    def write_byte(self, cmd, rs, wait_upper=0.001, wait_lower=0.001):
        k = K if self.backlight else 0
        upper = cmd & 0xF0 | rs | k
        lower = cmd << 4 & 0xF0 | rs | k
        self.bus.write_byte(self.i2c_address, upper | 0b00000100)
        #time.sleep(0.0001)
        self.bus.write_byte(self.i2c_address, upper & 0b11111011)
        time.sleep(wait_upper)
        self.bus.write_byte(self.i2c_address, lower | 0b00000100)
        #time.sleep(0.0001)
        self.bus.write_byte(self.i2c_address, lower & 0b11111011)
        time.sleep(wait_lower)

    def command_display(self, display, cursor, blink):
        self.write_byte(cmd['display'] | display << 2 | cursor << 1 | blink, rs['cmd'])
        self.display = display
        self.cursor = cursor
        self.blink = blink

    def write_text(self, text:str) -> None:
        '''
        Writes text starting at the cursor position and move the cursor to the
        end of the written text. If the cursor is outside the display, the text
        is written starting at the beginning of the current row.

        Parameters
        ----------
        text : str
        '''
        self.write_bytes(bytes(text, encoding='utf-8'))

    def write_bytes(self, btext:bytes) -> None:
        '''
        Writes text in bytes starting at the cursor position and move the cursor
        to the end of the written text. If the cursor is outside the display,
        the text is written starting at the beginning of the current row.

        Parameters
        ----------
        btext : bytes
            Text in bytes
        '''
        col = (self.col - self.shift) % BUFF_SIZE
        if not (0 <= col < LCD_COLS):
            col = 0
        self.write_bytes_at(btext, self.row, col)

    def write_text_at(self, text:str, row:int, col:int=0) -> None:
        '''
        Writes text starting at the specified display position and move the
        cursor to the end of the written text.

        Parameters
        ----------
        text : str
        row : int
            Valid range: 0-1
        col : int
            Valid range: 0-15

        Raises
        ------
        ValueError
            If row or col is out of the range.
        '''
        self.write_bytes_at(bytes(text, encoding='utf-8'), row, col)

    def write_bytes_at(self, btext:bytes, row:int, col:int=0) -> None:
        '''
        Writes text in bytes starting at the specified display position and move
        the cursor to the end of the written text.

        Parameters
        ----------
        btext : bytes
            Text in bytes
        row : int
            Valid range: 0-1
        column : int
            Valid range: 0-15

        Raises
        ------
        ValueError
            If row or col is out of the range.
        '''
        if not (0 <= row < LCD_ROWS):
            message = f'Invalid parameter row={row} was specified. It should be 0 to {LCD_ROWS - 1}.'
            raise ValueError(message)
        if not (0 <= col < LCD_COLS):
            message = f'Invalid parameter col={col} was specified. It should be 0 to {LCD_COLS - 1}.'
            raise ValueError(message)

        len_btext = len(btext)
        start = 0
        col = (self.shift + col) % BUFF_SIZE
        shift_rightedge = (self.shift + LCD_COLS - 1) % BUFF_SIZE

        while len_btext > 0:
            if col > shift_rightedge:
                len_to_write = min(len_btext, BUFF_SIZE - col)
            else:
                len_to_write = min(len_btext, shift_rightedge - col + 1)
            end = start + len_to_write
            self.write_bytes_buffer_at(btext[start : end], row, col)

            len_btext -= len_to_write
            start = end
            col = (col + len_to_write) % BUFF_SIZE
            if col == shift_rightedge + 1:
                col = self.shift
                row = (row + 1) % LCD_ROWS

        self.set_cursor_buffer(row, col)

    def write_text_alignment(
            self, text:str, row:int, alignment:LCDAlignment=LCDAlignment.LEFT, fill_space:bool=True) -> None:
        '''
        Writes text on the specified row with left, center, or right alignment
        on the display. The cursor is moved to the end of the written text.

        Parameters
        ----------
        text : str
        row : int
            Valid range: 0-1
        alignment : LCDAlignment
            LEFT, CENTER, or RIGHT
        clear : bool
            True to clear any parts other than the text with a space character,
            False to leave them unchanged.

        Raises
        ------
        ValueError
            If row is out of the range.
        '''
        self.write_bytes_alignment(bytes(text, encoding='utf-8'), row, alignment, fill_space)

    def write_bytes_alignment(
            self, btext:bytes, row:int, alignment:LCDAlignment=LCDAlignment.LEFT, fill_space:bool=True) -> None:
        '''
        Writes text in bytes on the specified row with left, center, or right
        alignment on the display. The cursor is moved to the end of the written
        text.

        Parameters
        ----------
        btext : bytes
            Text in bytes
        row : int
            Valid range: 0-1
        alignment : LCDAlignment
            LEFT, CENTER, or RIGHT
        clear : bool
            True to clear any parts other than the text with a space character,
            False to leave them unchanged.

        Raises
        ------
        ValueError
            If row is out of the range.
        '''
        if fill_space or len(btext) > LCD_COLS:
            match alignment:
                case LCDAlignment.LEFT:
                    btext = (btext + b'\x20' * LCD_COLS)[: LCD_COLS]
                case LCDAlignment.CENTER:
                    btext = b'\x20' * LCD_COLS + btext + b'\x20' * LCD_COLS
                    start = (len(btext) - LCD_COLS) // 2
                    btext = btext[start : start + LCD_COLS]
                case LCDAlignment.RIGHT:
                    btext = (b'\x20' * LCD_COLS + btext)[-LCD_COLS :]
            col = 0
        else:
            match alignment:
                case LCDAlignment.LEFT:
                    col = 0
                case LCDAlignment.CENTER:
                    col = (LCD_COLS - len(btext)) // 2
                case LCDAlignment.RIGHT:
                    col = LCD_COLS - len(btext)

        self.write_bytes_at(btext, row, col)

    def write_text_buffer(self, text:str) -> None:
        '''
        Writes text starting at the cursor position and move the cursor to the
        end of the written text.

        Parameters
        ----------
        text : str
        '''
        self.write_bytes_buffer(bytes(text, encoding='utf-8'))

    def write_bytes_buffer(self, btext:bytes) -> None:
        '''
        Writes text in bytes starting at the cursor position and move the cursor
        to the end of the written text.

        Parameters
        ----------
        btext : bytes
            Text in bytes
        '''
        self.write_bytes_buffer_at(btext, self.row, self.col)

    def write_text_buffer_at(self, text:str, row:int, col:int=0) -> None:
        '''
        Writes text starting at the specified buffer position and move the
        cursor to the end of the written text.

        Parameters
        ----------
        text : str
        row : int
            Valid range: 0-1
        col : int
            Valid range: 0-39

        Raises
        ------
        ValueError
            If row or col is out of the range.
        '''
        self.write_bytes_buffer_at(bytes(text, encoding='utf-8'), row, col)

    def write_bytes_buffer_at(self, btext:bytes, row:int, col:int=0) -> None:
        '''
        Writes text in bytes starting at the specified buffer position and move
        the cursor to the end of the written text.

        Parameters
        ----------
        btext : bytes
            Text in bytes
        row : int
            Valid range: 0-1
        col : int
            Valid range: 0-39

        Raises
        ------
        ValueError
            If row or col is out of the range.
        '''
        if not (0 <= row < LCD_ROWS):
            message = f'Invalid parameter row={row} was specified. It should be 0 to {LCD_ROWS - 1}.'
            raise ValueError(message)
        if not (0 <= col < BUFF_SIZE):
            message = f'Invalid parameter col={col} was specified. It should be 0 to {BUFF_SIZE - 1}.'
            raise ValueError(message)
        address = (DDRAM_ADDR_0 if row == 0 else DDRAM_ADDR_1) + col
        self.write_byte(cmd['ddram'] | address, rs['cmd'])      # set ddram address to write text

        length = len(btext)
        for i in range(length):
            self.write_byte(btext[i], rs['data'])
        col = col + length
        self.row = (row + col // BUFF_SIZE) % LCD_ROWS
        self.col = col % BUFF_SIZE

    def clear_all(self) -> None:
        '''
        Clears the entire buffer by filling it with space characters, reset the
        buffer position to its initial state, and set the cursor to the top-left
        corner of the display.
        '''
        self.write_byte(cmd['clear'], rs['cmd'], wait_lower=0.002)
        self.shift = 0
        self.row = 0
        self.col = 0

    def clear_row(self, row:int) -> None:
        '''
        Clears the display of the specified row by filling it with space
        characters, and set the cursor to the beginning of that row.

        Parameters
        ----------
        row : int
            Valid range: 0-1

        Raises
        ------
        ValueError
            If row is out of the range.
        '''
        self.clear(row, 0, LCD_COLS)
        self.set_cursor_home(row)

    def clear(self, row:int, col:int=0, length:int=0) -> None:
        '''
        Clears a specified length in the display by overwriting it with space
        characters, starting at the specified display position. Then move the
        cursor to the end of the written space characters.

        Parameters
        ----------
        row : int
            Valid range: 0-1
        col : int
            Valid range: 0-15
        length : int
            Valid range: 1- . If 0 is specified, the display is cleared to the end.

        Raises
        ------
        ValueError
            If row, col, or length is out of the range.
        '''
        if length < 0:
            message = f'Invalid parameter length={length} was specified. It should be greater than or equal to 0.'
            raise ValueError(message)
        if length == 0:
            length = LCD_COLS - col
        else:
            length = min(length, LCD_COLS * 2)

        self.write_bytes_at(bytes([0x20]) * length, row, col)

    def clear_row_buffer(self, row:int) -> None:
        '''
        Clears the buffer of the specified row by filling it with space
        characters, reset the buffer position to its initial state, and set the
        cursor to the beginning of that row.

        Parameters
        ----------
        row : int
            Valid range: 0-1

        Raises
        ------
        ValueError
            If row is out of the range.
        '''
        self.clear_buffer(row, 0, BUFF_SIZE)
        self.set_buffer_home(row)

    def clear_buffer(self, row:int, col:int=0, length:int=0) -> None:
        '''
        Clears a specified length in the buffer by overwriting it with space
        characters, starting at the specified buffer position. Then move the
        cursor to the end of the written space characters.

        Parameters
        ----------
        row : int
            Valid range: 0-1
        col : int
            Valid range: 0-39
        length : int
            Valid range: 1- . If 0 is specified, the buffer is cleared to the end.

        Raises
        ------
        ValueError
            If row, col, or length is out of the range.
        '''
        if length < 0:
            message = f'Invalid parameter length={length} was specified. It should be greater than or equal to 0.'
            raise ValueError(message)
        if length == 0:
            length = BUFF_SIZE - col
        else:
            length = min(length, BUFF_SIZE * 2)

        self.write_bytes_buffer_at(bytes([0x20]) * length, row, col)

    def set_home(self) -> None:
        '''
        Resets the buffer position to its initial state, and set the cursor to
        the top-left corner of the display.
        '''
        self.write_byte(cmd['home'], rs['cmd'], wait_lower=0.002)
        self.shift = 0
        self.row = 0
        self.col = 0

    def set_cursor_home(self, row:int=0) -> None:
        '''
        Sets the cursor to the beginning of the specified row.

        Parameters
        ----------
        row : int
            Valid range: 0-1

        Raises
        ------
        ValueError
            If row is out of the range.
        '''
        self.set_cursor(row, 0)

    def set_cursor(self, row:int, col:int=0) -> None:
        '''
        Sets the cursor to the specified display position.

        Parameters
        ----------
        row : int
            Valid range: 0-1
        col : int
            Valid range: 0-15

        Raises
        ------
        ValueError
            If row or col is out of the range.
        '''
        if not (0 <= row < LCD_ROWS):
            message = f'Invalid parameter row={row} was specified. It should be 0 to {LCD_ROWS - 1}.'
            raise ValueError(message)
        if not (0 <= col < LCD_COLS):
            message = f'Invalid parameter col={col} was specified. It should be 0 to {LCD_COLS - 1}.'
            raise ValueError(message)
        self.set_cursor_buffer(row, (self.shift + col) % BUFF_SIZE)

    def move_cursor(self, offset:int=1) -> None:
        '''
        Moves the cursor by the specified amount. If the cursor goes off the
        display, it will stay at the left or right edge of the display.

        Parameters
        ----------
        offset : int
            Positive values move to the right, and negative values move to the
            left.
        '''
        col = (self.col - self.shift + offset) % BUFF_SIZE
        if col >= LCD_COLS:
            col = 0 if offset < 0 else LCD_COLS - 1
        self.set_cursor(self.row, col)

    def set_buffer_home(self, row:int=0) -> None:
        '''
        Resets the buffer position to its initial state, and set the cursor to
        the beginning of the specified row.

        Parameters
        ----------
        row : int
            Valid range: 0-1

        Raises
        ------
        ValueError
            If row is out of the range.
        '''
        self.set_cursor_buffer(row, 0)
        self.set_buffer(0)

    def set_cursor_buffer(self, row:int, col:int=0) -> None:
        '''
        Sets the cursor to the specified buffer position.

        Parameters
        ----------
        row : int
            Valid range: 0-1
        col : int
            Valid range: 0-39

        Raises
        ------
        ValueError
            If row or col is out of the range.
        '''
        if not (0 <= row < LCD_ROWS):
            message = f'Invalid parameter row={row} was specified. It should be 0 to {LCD_ROWS - 1}.'
            raise ValueError(message)
        if not (0 <= col < BUFF_SIZE):
            message = f'Invalid parameter col={col} was specified. It should be 0 to {BUFF_SIZE - 1}.'
            raise ValueError(message)
        address = (DDRAM_ADDR_0 if row == 0 else DDRAM_ADDR_1) + col
        self.write_byte(cmd['ddram'] | address, rs['cmd'])
        self.row = row
        self.col = col

    def move_cursor_buffer(self, offset:int=1) -> None:
        '''
        Moves the cursor by the specified amount.

        Parameters
        ----------
        offset : int
            Positive values move to the right, and negative values move to the left.
        '''
        self.set_cursor_buffer(self.row, (self.col + offset) % BUFF_SIZE)

    def set_buffer(self, col:int=0) -> None:
        '''
        Shifts the specified buffer position to the left edge of the display.

        Parameters
        ----------
        col : int
            Valid range: 0-39

        Raises
        ------
        ValueError
            If col is out of the range.
        '''
        if not (0 <= col < BUFF_SIZE):
            message = f'Invalid parameter col={col} was specified. It should be 0 to {BUFF_SIZE - 1}.'
            raise ValueError(message)
        self.move_buffer(col - self.shift)

    def move_buffer(self, offset:int=1) -> None:
        '''
        Shifts the buffer by the specified amount.

        Parameters
        ----------
        offset : int
            Positive values shift to the left, and negative values shift to the
            right.
        '''
        direction = 0x04 if offset < 0 else 0x00
        amount = abs(offset) % BUFF_SIZE

        for i in range(amount):
            self.write_byte(cmd['cursor'] | 0x08 | direction, rs['cmd'])
        self.shift = (self.shift + offset) % BUFF_SIZE

    def set_display(self, enabled:bool=True) -> None:
        '''
        Turns the display on or off.

        Parameters
        ----------
        enabled : bool
            True to turn on, False to turn off.
        '''
        self.command_display(enabled, self.cursor, self.blink)

    def set_backlight(self, enabled:bool=True) -> None:
        '''
        Turns the backlight on or off.

        Parameters
        ----------
        backlight : bool
            True to turn on, False to turn off.
        '''
        self.backlight = enabled
        self.command_display(self.display, self.cursor, self.blink) # do something to trun backlight on or off.

    def set_cursor_attribute(self, show:bool=True, blink:bool=False) -> None:
        '''
        Sets the cursor visibility and blinking state.

        Parameters
        ----------
        show : bool
            True to show the cursor, False to hide it.
        blink : bool
            True to enable blinking, False to disable blinking.
        '''
        self.command_display(self.display, show, blink)

    def turn_off(self) -> None:
        '''
        Turns off the backlight, disable the display and cursor, and clear the
        buffer.
        '''
        self.set_backlight(False)                               # backlight off
        self.command_display(False, False, False)               # display off, cursor off, blinking off
        self.clear_all()

    def register_pattern(self, char_code:int, pattern:list) -> None:
        '''
        Registers a custom font pattern into CGRAM.

        Parameters
        ----------
        char_code : int
            Valid range: 0-7
        pattern : list
            An 8-element list representing the pattern for each font row.

        Raises
        ------
        ValueError
            If char_code is out of the range or pattern does not contain exactly
            8 elements.
        '''
        if not (0 <= char_code < 0x08):
            message = f'Invalid parameter char_code={char_code} was specified. It should be 0 to 7.'
            raise ValueError(message)
        if not (len(pattern) == CUSTOM_FONT_HEIGHT):
            message = f'Invalid parameter pattern={pattern} was specified. The number of elements must be {CUSTOM_FONT_HEIGHT}.'
            raise ValueError(message)
        self.write_byte(cmd['cgram'] | char_code * 8, rs['cmd'])    # set CGRAM address to write pattern

        for i in range(CUSTOM_FONT_HEIGHT):
            self.write_byte(pattern[i], rs['data'])
        self.set_cursor_buffer(self.row, self.col)

    def clear_pattern(self, char_code:int) -> None:
        '''
        Clears the custom font pattern registered in CGRAM.

        Parameters
        ----------
        char_code : int
            Valid range: 0x00-0x07

        Raises
        ------
        InvalidParameterError
            If code is out of the range.
        '''
        self.register_pattern(char_code, [0x00] * CUSTOM_FONT_HEIGHT)

    def get_row_count(self) -> int:
        '''
        Returns the number of display rows.

        Returns
        -------
        int
            The number of display rows (2).
        '''
        return LCD_ROWS

    def get_col_count(self) -> int:
        '''
        Returns the number of display columns.

        Returns
        -------
        int
            The number of display columns (16).
        '''
        return LCD_COLS

    def get_buffer_length(self) -> int:
        '''
        Returns the buffer length per row.

        Returns
        -------
        int
            The buffer length per row (40).
        '''
        return BUFF_SIZE

    def get_cursor(self) -> tuple[int, int]:
        '''
        Returns the current cursor position on the display as a (row, col)
        tuple.

        Returns
        -------
        tuple[int, int]
            A tuple (row, col) representing the cursor position (row: 0-1,
            col:0-15) or both are -1 if cursor is not on the display area.
        '''
        pos = self.row, (self.col - self.shift) % BUFF_SIZE
        if pos[1] >= LCD_COLS:
            pos = -1, -1
        return pos

    def get_cursor_buffer(self) -> tuple[int, int]:
        '''
        Returns the current cursor position on the buffer as a (row, col) tuple.

        Returns
        -------
        tuple[int, int]
            A tuple (row, col) representing the cursor position (row: 0-1,
            col: 0-39).
        '''
        return self.row, self.col

    def get_buffer(self) -> int:
        '''
        Returns the buffer position on the left edge of the display.

        Returns
        -------
        int
            The buffer position on the left edge of the display (0-39).
        '''
        return self.shift

    def close(self) -> None:
        '''
        Closes the I2C bus connection.
        '''
        self.bus.close()

    def demo(self) -> None:
        '''
        Fills the entire buffer with sample text for demonstration purposes.
        '''
        self.write_bytes_buffer_at(bytes(range(0x40, 0x68)), 0)
        self.write_text_buffer_at('0....+....1....+....2....+....3....+....', 1)

if __name__ == '__main__':
    print(LCD1602.__doc__)
