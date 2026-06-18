# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevsnfb.c

Ghostscript output device for the Sony NEWS framebuffer.

Key behavior:
- Defines the `sonyfb` monochrome printer-style device at 1024x1032 pixels, 100 DPI.
- Opens `/dev/fb` read/write and queries screen type with `FBIOCGETSCRTYPE`.
- Stores the visible rectangle from the framebuffer driver.
- Uses Ghostscript printer memory as the source bitmap.
- Builds an `sPrimRect` structure with a memory bitmap source and framebuffer destination.
- Copies the rendered page into the framebuffer via `FBIOCRECTANGLE`.
- Closes the framebuffer descriptor on device close.
- Completes output pages with `gx_finish_output_page`.

Notable dependencies:
- Ghostscript printer API: `gdevprn.h`.
- Sony NEWS framebuffer headers and ioctls: `newsiop/framebuf.h`, `FBIOCGETSCRTYPE`, `FBIOCRECTANGLE`.

Research notes:
- This is direct framebuffer display output presented through printer-device buffering.
- It uses global framebuffer state (`fb_file`, `prect`).
- Several system functions are used without local includes for their prototypes in this file.
