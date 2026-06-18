# File Research: sources/os/plan9/9front/sys/src/cmd/vcrop.c

Purpose: Interactive Plan 9 image cropper.

Key behavior:
- Reads an image from stdin or a named file and displays it in a draw window.
- Left-drag pans the image; middle-click invokes rectangle crop; right-click opens a menu with crop, undo, save, and exit.
- `crop` clamps the selected rectangle to image bounds, creates a new image, stores the previous image for one-level undo, and resets position.
- `save` prompts for an output filename and writes the current image.
- Handles window resize and Delete-key exit.

Dependencies:
- Uses Plan 9 draw, mouse, keyboard, thread, image read/write, and `getrect`/`enter`.

Notable details:
- Ignores tiny crop rectangles below a 5-pixel threshold in both dimensions.
