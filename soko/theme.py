from adafruit_bitmap_font import bitmap_font

BRIGHT = 0xE0E0E0
MID    = 0x808080
DIM    = 0x606060
FAINT  = 0x202020
GREEN  = 0x006000

# Airline logos are 20x16 BMPs drawn at 2x, so 40x32 on screen.
LOGO_SCALE = 2
# Source bitmap size, before scaling. Used to work out where text starts.
LOGO_W, LOGO_H = 23, 18
# Top-left corner of the logo, in screen pixels.
LOGO_X, LOGO_Y = 4, 2

# Panel size.
WIDTH, HEIGHT = 128, 64

MARGIN_L, MARGIN_R = 4, 123

TEXT_SCALE = 1

TEXT_X = 52

# The positioning of the text rows.
ROW_1, ROW_2, ROW_3 = 10, 20, 30
ROW_4, ROW_5 = 54, 44

# Progress bar sits on the bottom edge. (61 pixels from the top)
BAR_Y = 61

FRAME_SLEEP = 0.05
FONT = bitmap_font.load_font("/fonts/spleen.bdf")
