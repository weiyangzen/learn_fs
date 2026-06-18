# File Research: sources/os/plan9/9front/sys/src/cmd/mug.c

Interactive Plan 9 image tool for making 48x48 grayscale “mug”/face icons.

Key responsibilities:
- Reads an input image from a file or stdin, converts it to `GREY8`, and displays the original beside a gamma/black-white ramp and 48x48 previews.
- Maintains editing `State`: black point, white point, stretch, gamma, output depth, gamma table, and selected square crop rectangle.
- Downsamples the selected square to 48x48 using separable smoothing, value remapping, gamma correction, and optional error-diffusion dithering for low bit depths.
- Supports depths 8/4/2/1 through the button-3 menu.
- Provides undo by keeping prior state/image, reset, write-to-stdout, and exit.
- Lets the user drag/resize the crop rectangle using region-specific cursors.
- Lets the user drag the current face or saved face slots between the active preview and eight storage slots.
- Writes GREY1/GREY2 output as numeric initializer-style rows and GREY4/GREY8 output as a Plan 9 image.

Important interactions:
- Uses Plan 9 draw/event/cursor APIs heavily.
- Uses `readimage`, `writeimage`, `loadimage`, `unloadimage`, `allocimage`, and `rgb2cmap`.

Notable quirks:
- The code defines its own `min`, `max`, and `abs`.
- UI behavior is mouse-centric; keyboard events are ignored.
- Some comments acknowledge visual flashiness and heuristic control behavior.
