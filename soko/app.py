import board
import displayio
import framebufferio
import rgbmatrix
import terminalio
from adafruit_display_text import label


def run():
    displayio.release_displays()

    matrix = rgbmatrix.RGBMatrix(
        width=128, height=64, bit_depth=3,
        rgb_pins=[board.MTX_R1, board.MTX_G1, board.MTX_B1,
                  board.MTX_R2, board.MTX_G2, board.MTX_B2],
        addr_pins=[board.MTX_ADDRA, board.MTX_ADDRB, board.MTX_ADDRC,
                   board.MTX_ADDRD, board.MTX_ADDRE],
        clock_pin=board.MTX_CLK, latch_pin=board.MTX_LAT,
        output_enable_pin=board.MTX_OE)
    display = framebufferio.FramebufferDisplay(matrix)

    text_area = label.Label(
        font=terminalio.FONT,
        text="HELLO WORLD",
        color=0x0000FF,
    )
    text_area.x = 30
    text_area.y = 30

    display.root_group = text_area

    while True:
        pass
