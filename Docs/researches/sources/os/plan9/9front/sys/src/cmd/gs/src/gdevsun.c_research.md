# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevsun.c

Legacy Ghostscript SunView display driver.

Key behavior:
- Defines the `sunview` display device using SunView `Frame`, `Canvas`, and `Pixwin` APIs.
- Creates a SunView frame/canvas sized to the page dimensions and installs scrollbars.
- Detects monochrome, 8-bit pseudocolor, and 24/32-bit true-color displays.
- Configures Ghostscript color information according to display depth.
- For pseudocolor displays, allocates a private colormap named `GHOSTVIEW-<pid>`.
- Preallocates black/white and an RGB color cube, then allocates additional exact colors on demand until the colormap is full.
- Encodes true-color pixels directly into a packed BGR-style color index.
- Maps color indices back to RGB values from either the colormap or packed true-color fields.
- Implements rectangle fill, monochrome bitmap copy, color bitmap copy, line drawing, sync, and close.
- Uses Sun Pixrect operations (`pw_write`, `pw_stencil`, `pw_vector`) for drawing.
- On little-endian hosts, reverses bitmap bits temporarily before SunView stencil operations and then restores them.
- Interposes a destroy callback to veto user window close actions that would confuse device bookkeeping.

Notable dependencies:
- SunView and SunWindow headers: `suntool/sunview.h`, `suntool/canvas.h`, `sunwindow/cms_mono.h`.
- Ghostscript device/product definitions: `gxdevice.h`, `gscdefs.h`, `gsmatrix.h`.
- C heap allocation through `malloc_.h`.

Research notes:
- The file is display GUI integration, not filesystem code.
- `sun_copy_mono` intentionally mutates a `const byte *` bitmap in place temporarily, with a comment acknowledging the hazard.
- Colormap exhaustion returns `gx_no_color_index` to trigger Ghostscript dithering; a comment warns this can loop if Ghostscript requests non-cube colors.
