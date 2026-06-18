# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevs3ga.c

Purpose: Ghostscript display driver for S3 86C911/S3 VGA hardware acceleration.

Key behavior:
- Defines `gs_s3vga_device` using shared SVGA support and VESA mode get/set hooks.
- Supports fixed enhanced modes 640x480, 800x600, and 1024x768; uses a 1024-pixel framebuffer raster.
- Tracks a bitmap/character cache in off-screen memory with 32x32 cells.
- Drives S3 registers directly through port I/O for rectangle fills and mono bitmap copies.
- `s3_fill_rectangle` emits hardware rectangle fill commands.
- `s3_copy_mono` handles transparent foreground/background colors, source bit alignment, direct CPU-to-screen transfer, and cached screen-to-screen character blits.

Important dependencies:
- PC framebuffer/SVGA support: `gdevpcfb.h`, `gdevsvga.h`.
- Low-level port I/O macros/functions from the PC framebuffer layer.

Notable risks / findings:
- Hardware-specific driver using direct I/O ports; not portable and only meaningful on old S3 VGA environments.
- Cache placement assumes off-screen memory at y offset 768 and a 1024-pixel raster.
