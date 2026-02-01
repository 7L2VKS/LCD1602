# LCD1602 I2C Python Library

A Python library for operating an LCD1602 (16 x 2 character display) device over an I2C interface. This library has been confirmed to work on Raspberry Pi 3 model B and 5.

## Overview

This library provides a set of methods for controlling an LCD1602 device, including cursor movement, text displaying, text alignment handling, buffer manipulation, display configuration, and CGRAM pattern (custom font) registration.

The LCD1602 display consists of 2 rows x 16 columns, backed by a 40-character buffer per row. The library internally tracks the cursor position, buffer shift amount allowing the user to query cursor and buffer positions at any time.

5 x 8 dot custom fonts may be registered in CGRAM using character codes in the range 0x00 to 0x07.

* **`LCD1602.py`**: The main class for the device control.
* **`LCDDemo.py`**: Sample and demo script for using this library.

## Preparation

Before using this library, you need to enable the I2C interface, wire the device, and identify the device address.

### 1. Enable I2C
On Raspberry Pi, use `sudo raspi-config` to enable I2C under **Interface Options** > **I2C**.

### 2. Wiring
Connect I2C module on the LCD1602 to your Raspberry Pi using the following pin mapping:

| LCD1602 (I2C) | Raspberry Pi Pin | Function |
| :--- | :--- | :--- |
| **GND** | GND (e.g. Pin 6) | Ground |
| **VCC** | 5V (e.g. Pin 2) | Power (5V) |
| **SDA** | GPIO 2 (SDA, Pin 3) | I2C Data |
| **SCL** | GPIO 3 (SCL, Pin 5) | I2C Clock |

### 3. Install Dependencies
This library requires the `smbus2` package for I2C communication. It is usually installed by default on Raspberry Pi OS, but if it is not, install it with the following command.

```bash
pip install smbus2
```

### 4. Identify I2C Address

If you don't have it installed, install `i2c-tools`:

```bash
sudo apt install i2c-tools
```

Run the following command to find the address of your device:

```bash
i2cdetect -y 1
```

The hex value shown in the table (e.g. `27`) is the I2C address.

## Quick Start

Place `LCD1602.py` in your project directory and run the following in Python REPL:

```python
>>> from LCD1602 import LCD1602
>>> # Replace 0x27 with the address from i2cdetect
>>> with LCD1602(0x27) as lcd:
...     lcd.demo()
```

Alternatively, run the demo script to see various features in action. Before running it, change the I2C address in the script to the address you confirmed in the step above.

```bash
python LCDDemo.py
```

## API Reference

### `LCD1602` Class

The main controller class for the LCD1602 device.

#### Constructor

**`LCD1602(i2c_address, cursor=True, blink=False, backlight=True)`**

* **`i2c_address`** (int): The I2C address of the LCD1602 device.
* **`cursor`** (bool): Whether the cursor is initially enabled.
* **`blink`** (bool): Whether the cursor blinking mode is initially enabled.
* **`backlight`** (bool): Whether the backlight is initially turned on.

If you do not use a context manager (`with` statement), you can close the I2C bus connection by calling the close() method last.

---

### Text Display Methods

#### **`write_text(text)`**
Writes text starting at the cursor position and move the cursor to the end of the written text. If the cursor is outside the display, the text is written starting at the beginning of the current row.
* **`text`** (str): String to display.

#### **`write_bytes(btext)`**
Writes text in bytes starting at the cursor position and move the cursor to the end of the written text. If the cursor is outside the display, the text is written starting at the beginning of the current row.
* **`btext`** (bytes): Bytes to display.

#### **`write_text_at(text, row, col=0)`**
Writes text starting at the specified display position and move the cursor to the end of the written text.
* **`text`** (str): String to display.
* **`row`** (int): Row index (0 or 1).
* **`col`** (int): Column index (Valid range: 0-15).
* **Raises**: `ValueError` if `row` or `col` is out of the range.

#### **`write_bytes_at(btext, row, col=0)`**
Writes text in bytes starting at the specified display position and move the cursor to the end of the written text.
* **`btext`** (bytes): Bytes to display.
* **`row`** (int): Row index (0 or 1).
* **`col`** (int): Column index (Valid range: 0-15).
* **Raises**: `ValueError` if `row` or `col` is out of the range.

#### **`write_text_alignment(text, row, alignment=LCDAlignment.LEFT, fill_space=True)`**
Writes text on the specified row with left, center, or right alignment on the display. The cursor is moved to the end of the written text.
* **`text`** (str): String to display.
* **`row`** (int): Row index (0 or 1).
* **`alignment`** (LCDAlignment): `LEFT`, `CENTER`, or `RIGHT`.
* **`fill_space`** (bool): `True` to clear any parts other than the text with space characters, `False` to leave them unchanged.
* **Raises**: `ValueError` if `row` is out of the range.

#### **`write_bytes_alignment(btext, row, alignment=LCDAlignment.LEFT, fill_space=True)`**
Writes text in bytes on the specified row with left, center, or right alignment on the display. The cursor is moved to the end of the written text.
* **`btext`** (bytes): Bytes to display.
* **`row`** (int): Row index (0 or 1).
* **`alignment`** (LCDAlignment): `LEFT`, `CENTER`, or `RIGHT`.
* **`fill_space`** (bool): `True` to clear any parts other than the text with space characters, `False` to leave them unchanged.
* **Raises**: `ValueError` if `row` is out of the range.

#### **`write_text_buffer(text)`**
Writes text starting at the cursor position and move the cursor to the end of the written text.
* **`text`** (str): String to display.

#### **`write_bytes_buffer(btext)`**
Writes text in bytes starting at the cursor position and move the cursor to the end of the written text.
* **`btext`** (bytes): Bytes to display.

#### **`write_text_buffer_at(text, row, col=0)`**
Writes text starting at the specified buffer position and move the cursor to the end of the written text.
* **`text`** (str): String to display.
* **`row`** (int): Row index (0 or 1).
* **`col`** (int): Column index (Valid range: 0-39).
* **Raises**: `ValueError` if `row` or `col` is out of the range.

#### **`write_bytes_buffer_at(btext, row, col=0)`**
Writes text in bytes starting at the specified buffer position and move the cursor to the end of the written text.
* **`btext`** (bytes): Bytes to display.
* **`row`** (int): Row index (0 or 1).
* **`col`** (int): Column index (Valid range: 0-39).
* **Raises**: `ValueError` if `row` or `col` is out of the range.

#### **`demo()`**
Fills the entire buffer with sample text for demonstration purposes.

---

### Clear Methods

#### **`clear_all()`**
Clears the entire buffer by filling it with space characters, reset the buffer position to its initial state, and set the cursor to the top-left corner of the display.

#### **`clear_row(row)`**
Clears the display of the specified row by filling it with space characters, and set the cursor to the beginning of that row.
* **`row`** (int): Row index (0 or 1).
* **Raises**: `ValueError` if `row` is out of the range.

#### **`clear(row, col=0, length=0)`**
Clears a specified length in the display by overwriting it with space characters, starting at the specified display position. Then move the cursor to the end of the written space characters.
* **`row`** (int): Row index (0 or 1).
* **`col`** (int): Column index (Valid range: 0-15).
* **`length`** (int): The length to clear (Valid range: 1-). If 0 is specified, the display is cleared to the end.
* **Raises**: `ValueError` if `row`, `col`, or `length` is out of the range.

#### **`clear_row_buffer(row)`**
Clears the buffer of the specified row by filling it with space characters, reset the buffer position to its initial state, and set the cursor to the beginning of that row.
* **`row`** (int): Row index (0 or 1).
* **Raises**: `ValueError` if `row` is out of the range.

#### **`clear_buffer(row, col=0, length=0)`**
Clears a specified length in the buffer by overwriting it with space characters, starting at the specified buffer position. Then move the cursor to the end of the written space characters.
* **`row`** (int): Row index (0 or 1).
* **`col`** (int): Column index (Valid range: 0-39).
* **`length`** (int): The length to clear (Valid range: 1-). If 0 is specified, the buffer is cleared to the end.
* **Raises**: `ValueError` if `row`, `col`, or `length` is out of the range.

---

### Cursor and Buffer Positioning Methods

#### **`set_home()`**
Resets the buffer position to its initial state, and set the cursor to the top-left corner of the display.

#### **`set_cursor_home(row=0)`**
Sets the cursor to the beginning of the specified row.
* **`row`** (int): Row index (0 or 1).
* **Raises**: `ValueError` if `row` is out of the range.

#### **`set_cursor(row, col=0)`**
Sets the cursor to the specified display position.
* **`row`** (int): Row index (0 or 1).
* **`col`** (int): Column index (Valid range: 0-15).
* **Raises**: `ValueError` if `row` or `col` is out of the range.

#### **`move_cursor(offset=1)`**
Moves the cursor by the specified amount. If the cursor goes off the display, it will stay at the left or right edge of the display.
* **`offset`** (int): Amount of movement. Positive values move to the right, and negative values move to the left.

#### **`set_buffer_home(row=0)`**
Resets the buffer position to its initial state, and set the cursor to the beginning of the specified row.
* **`row`** (int): Row index (0 or 1).
* **Raises**: `ValueError` if `row` is out of the range.

#### **`set_cursor_buffer(row, col=0)`**
Sets the cursor to the specified buffer position.
* **`row`** (int): Row index (0 or 1).
* **`col`** (int): Column index (Valid range: 0-39).
* **Raises**: `ValueError` if `row` or `col` is out of the range.

#### **`move_cursor_buffer(offset=1)`**
Moves the cursor by the specified amount.
* **`offset`** (int): Amount of movement. Positive values move to the right, and negative values move to the left.

#### **`set_buffer(col=0)`**
Shifts the specified buffer position to the left edge of the display.
* **`col`** (int): Column index (Valid range: 0-39).
* **Raises**: `ValueError` if `col` is out of the range.

#### **`move_buffer(offset1)`**
Shifts the buffer by the specified amount.
* **`offset`** (int): Amount of shift. Positive values shift to the right, and negative values shift to the left.

---

### Mode Setting Methods

#### **`set_display(enabled=True)`**
Turns the display on or off.
* **`enabled`** (bool): `True` to turn on, `False` to turn off.

#### **`set_backlight(enabled=True)`**
Turns the backlight on or off.
* **`enabled`** (bool): `True` to turn on, `False` to turn off.

#### **`set_cursor_attribute(show=True, blink=False)`**
Sets the cursor visibility and blinking state.
* **`show`** (bool): `True` to show the cursor, `False` to hide it.
* **`blink`** (bool): `True` to enable blinking, `False` to disable blinking.

---

### Custom Font Methods

#### **`register_pattern(char_code, pattern)`**
Registers a custom font pattern into CGRAM.
* **`char_code`** (int): Character code to register (Valid range: 0 to 7).
* **`pattern`** (list): An 8-element list representing the font pattern.
* **Raises**: `ValueError` If `char_code` is out of the range or `pattern` does not contain exactly 8 elements.

To define a customer font, specify the binary value of each line of the font pattern. Since the font size is 5x8 dots, bits 5-7 of each line are not used. Also, since the last line is the cursor line, set it to 0x00.

Example: Font pattern and specified value
```
bit 765 43210    Binary       Hexadecimal
    ... ..#..    0000 0100    0x04
    ... #...#    0001 0001    0x11
    ... .###.    0000 1110    0x0E
    ... #####    0001 1111    0x1F
    ... .###.    0000 1110    0x0E
    ... #...#    0001 0001    0x11
    ... ..#..    0000 0100    0x04
    ... .....    0000 0000    0x00 (line for cursor)
```
In the above case, set the arguments of register_pattern() as follows: 
```
lcd.register_pattern(0, [0x04, 0x11, 0x0E, 0x1F, 0x0E, 0x11, 0x04, 0x00])
```

#### **`clear_pattern(char_code)`**
Clears the custom font pattern registered in CGRAM.
* **`char_code`** (int): Character code to clear (Valid range: 0 to 7).
* **Raises**: `ValueError` if `char_code` is out of the range.

---

### State Query Methods

#### **`get_row_count()`**
Returns the number of display rows.
* **Returns** (int): The number of display rows (2).

#### **`get_col_count()`**
Returns the number of display columns.
* **Returns** (int): The number of display columns (16).

#### **`get_buffer_length()`**
Returns the buffer length per row.
* **Returns** (int): The buffer length per row (40).

#### **`get_cursor()`**
Returns the current cursor position on the display as a (row, col) tuple.
* **Returns** (tuple[int, int]): A tuple (row, col) representing the cursor position (row: 0-1, col: 0-15) or both are -1 if cursor is not on the display area.

#### **`get_cursor_buffer()`**
Returns the current cursor position on the buffer as a (row, col) tuple.
* **Returns** (tuple[int, int]): A tuple (row, col) representing the cursor position (row: 0-1, col: 0-39).

#### **`get_buffer()`**
Returns the buffer position on the left edge of the display.
* **Returns** (int): The buffer position on the left edge of the display (0-39).

---

### Other Methods

#### **`turn_off()`**
Turns off the backlight, disables the display and cursor, and clears the buffer.

#### **`close()`**
Closes the I2C bus connection. If you don't use a context manager (`with` statement), call this last.

## License

This library is released under the MIT license.
