# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevsnfb.c

Purpose: Sony NEWS framebuffer output device for Ghostscript.

Key behavior:
- Defines `sonyfb`, a 1-bit printer-style framebuffer device sized for a 1024x1032-ish 100 dpi surface.
- Opens `/dev/fb`, obtains screen type with `FBIOCGETSCRTYPE`, and stores the visible rectangle.
- On output, maps Ghostscript printer memory as a monochrome memory bitmap.
- Builds a `sPrimRect` operation from memory bitmap to framebuffer bitmap using `BF_S`.
- Issues `FBIOCRECTANGLE` to copy the rendered page into the framebuffer, then finishes the Ghostscript output page.

Important dependencies:
- Sony NEWS framebuffer API: `<newsiop/framebuf.h>`.
- Ghostscript printer memory buffer internals.

Notable risks / findings:
- If `/dev/fb` open or ioctls fail, the code prints `perror` but may continue to printer open/output paths.
- Uses GCC-style `typeof`.
