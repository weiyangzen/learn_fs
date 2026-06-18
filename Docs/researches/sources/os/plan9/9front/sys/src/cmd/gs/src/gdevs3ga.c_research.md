# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevs3ga.c

Ghostscript SVGA display driver for S3 86C911 graphics hardware.

Key behavior:
- Defines the `s3vga` device using the shared SVGA device framework.
- Supports VESA modes for 640x480, 800x600, and 1024x768, with enhanced modes using a 1024-pixel raster.
- Uses direct I/O port programming for S3 accelerator registers.
- Implements accelerated rectangle fill through foreground color, mix mode, and rectangle command setup.
- Implements monochrome bitmap copy, including transparent zero/one color handling.
- Maintains a character bitmap cache in off-screen display memory at y=768, keyed by `gx_bitmap_id`.
- Uploads cached glyph bitmaps to off-screen memory and later copies them back to the visible screen with display-to-display blits.

Notable dependencies:
- Shared PC framebuffer/SVGA code: `gdevpcfb.h`, `gdevsvga.h`.
- External SVGA mode functions from `gdevsvga.c`: `vesa_get_mode`, `vesa_set_mode`.
- Low-level port I/O helpers/macros such as `inport`, `outport`, and `outportb`.

Research notes:
- The file is legacy hardware display code that assumes direct VGA/S3 register access.
- `draw_line` is explicitly disabled with comments saying it does not work.
- It is display hardware support, not filesystem code.
