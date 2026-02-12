# LCD1602 demo (sample code how to use LCD1602 class)

from lcd1602 import LCD1602, LCDAlignment
from time import sleep

COLS = 16
BUFF = 40

text1 = 'ABCDEFGHabcdefgh'
text2 = b'\xB1\xB2\xB3\xB4\xB5\xB6\xB7\xB8\xA7\xA8\xA9\xAA\xAB\xAC\xAD\xAE'
text3 = '0....+....1....+....2....+....3....+....'

def main():
    with LCD1602(0x27) as lcd:          # Replace the argument 0x27 to match the output
                                        # result of command "i2cdetect -y 1"
        lcd.write_text('[ LCD1602 DEMO ]')
        sleep(3)

        #
        # write_text(), write_bytes()
        #
        lcd.clear_all()                 # cursor moves to row 0, col 0 on the display
        lcd.write_text(text1[0 : 5])

        lcd.set_cursor(1, 5)            # set cursor at row 1, col 5 on the display
        lcd.write_bytes(text2[0 : 5])

        sleep(3)

        lcd.set_cursor_attribute(False) # set cursor invisible

        #
        # write_text_at(), write_bytes_at()
        #
        lcd.clear_all()
        col_on_disp = 0
        for t1, t2 in zip(text1, reversed(text2)):
            lcd.write_text_at(t1, 0, col_on_disp)
            lcd.write_bytes_at(bytes([t2]), 1, COLS - col_on_disp - 1)
            col_on_disp += 1
            sleep(0.2)

        sleep(3)

        #
        # write_text_alighment()
        #
        lcd.clear_all()
        lcd.write_text_alignment('Text Alignment', 0, LCDAlignment.CENTER)

        lcd.write_text_alignment('LEFT', 1, LCDAlignment.LEFT)
        sleep(1.5)

        lcd.write_text_alignment('CENTER', 1, LCDAlignment.CENTER)
        sleep(1.5)

        lcd.write_text_alignment('RIGHT', 1, LCDAlignment.RIGHT)
        sleep(3)

        #
        # write_text_buffer_at()
        #
        lcd.clear_all()
        lcd.write_text_buffer_at(text3, 1, 0)

        #
        # set_buffer(), move_buffer()
        #
        lcd.write_text_alignment('  Shift to Left', 0, LCDAlignment.LEFT)
        lcd.write_bytes_alignment(b'\x7F', 0, LCDAlignment.LEFT, fill_space=False)
                                        # do not clear the text (0x7F is a lift arrow)
        sleep(1.5)

        for col_on_buff in [6, 12, 18, 24]:
            lcd.set_buffer(col_on_buff)
            sleep(0.5)

        sleep(1.5)

        lcd.write_text_alignment('Shift to Right  ', 0, LCDAlignment.RIGHT)
        lcd.write_bytes_alignment(b'\x7E', 0, LCDAlignment.RIGHT, fill_space=False)
                                        # do not clear the text (0x7E is a right arrow)
        sleep(1.5)

        for i in range(4):
            lcd.move_buffer(-6)
            sleep(0.5)

        sleep(3)

        #
        # set_cursor(), move_cursor()
        #
        lcd.set_cursor_attribute(True)   # set cursor visible

        lcd.clear_all()
        lcd.write_text_alignment('Cursor Movement', 0, LCDAlignment.CENTER)

        pos_on_display = [(0, 0), (0, 4), (0, 8), (0, 12), (1, 15)]
                                         # list of position on the display
        for pos in pos_on_display:
            lcd.set_cursor(pos[0], pos[1])
            sleep(1)

        for i in range(16):
            lcd.move_cursor(-1)
            sleep(0.4)

        sleep(3)

        #
        # set_cursor_attribute()
        #
        lcd.clear_all()
        lcd.write_text_alignment('Cursor Style', 0, LCDAlignment.CENTER)

        lcd.write_text_at('Steady', 1, 2)
        lcd.set_cursor_home(1)

        sleep(3)

        lcd.write_text_at('Blinking', 1, 2)
        lcd.set_cursor_home(1)
        lcd.set_cursor_attribute(blink=True)

        sleep(3)

        lcd.set_cursor_attribute(False) # set cursor invisible

        #
        # register_pattern(), clear_pattern()
        #
        # To define a customer font, specify the binary value of each line of the font
        # pattern. Since the font size is 5x8 dots, bits 5-7 of each line are not used.
        # Also, since the last line is the cursor line, set it to 0x00.
        #
        # Example: Font pattern and specified value
        #
        # bit 765 43210    Binary       Hexadecimal
        #     ... ..#..    0000 0100    0x04
        #     ... #...#    0001 0001    0x11
        #     ... .###.    0000 1110    0x0E
        #     ... #####    0001 1111    0x1F
        #     ... .###.    0000 1110    0x0E
        #     ... #...#    0001 0001    0x11
        #     ... ..#..    0000 0100    0x04
        #     ... .....    0000 0000    0x00 (line for cursor)
        #
        # In the above case, set the arguments of register_pattern() as follows:
        #     lcd.register_pattern(0, [0x04, 0x11, 0x0E, 0x1F, 0x0E, 0x11, 0x04, 0x00])
        #
        lcd.clear_all()
        lcd.write_text_alignment('Custom Fonts', 0, LCDAlignment.CENTER)

        lcd.register_pattern(0, [0x04, 0x11, 0x0E, 0x1F, 0x0E, 0x11, 0x04, 0x00])
        lcd.register_pattern(1, [0x0C, 0x1E, 0x0C, 0x00, 0x06, 0x0F, 0x06, 0x00])
        lcd.register_pattern(2, [0x0E, 0x1F, 0x0E, 0x00, 0x15, 0x00, 0x15, 0x00])
        lcd.write_text_at('0:   1:   2:', 1, 1)
        lcd.write_bytes_at(b'\0', 1, 3)
        lcd.write_bytes_at(b'\1', 1, 8)
        lcd.write_bytes_at(b'\2', 1, 13)
        sleep(3)

        lcd.register_pattern(0, [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        lcd.register_pattern(1, [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x1F, 0x00])
        lcd.register_pattern(2, [0x00, 0x00, 0x00, 0x00, 0x00, 0x1F, 0x1F, 0x00])
        lcd.register_pattern(3, [0x00, 0x00, 0x00, 0x00, 0x1F, 0x1F, 0x1F, 0x00])
        lcd.register_pattern(4, [0x00, 0x00, 0x00, 0x1F, 0x1F, 0x1F, 0x1F, 0x00])
        lcd.register_pattern(5, [0x00, 0x00, 0x1F, 0x1F, 0x1F, 0x1F, 0x1F, 0x00])
        lcd.register_pattern(6, [0x00, 0x1F, 0x1F, 0x1F, 0x1F, 0x1F, 0x1F, 0x00])
        lcd.register_pattern(7, [0x1F, 0x1F, 0x1F, 0x1F, 0x1F, 0x1F, 0x1F, 0x00])

        chars = [4, 7, 3, 6, 2, 1, 0, 5]
        updown = [-1, 1, -1, 1, -1, 1, -1, -1]
        for _ in range(50):
            lcd.write_bytes_alignment(bytes(chars), 1, LCDAlignment.CENTER)
            for i, char in enumerate(chars):
                if char == 0 or char == 7:
                    updown[i] *= -1
                chars[i] += updown[i]

        sleep(3)

        for char_code in range(8):
            lcd.clear_pattern(char_code)

        #
        # turn_off()
        #
        lcd.clear_all()
        lcd.write_text_alignment('Enjoy !', 0, LCDAlignment.CENTER)

        sleep(3)

        lcd.turn_off()

if __name__ == '__main__':
    main()
