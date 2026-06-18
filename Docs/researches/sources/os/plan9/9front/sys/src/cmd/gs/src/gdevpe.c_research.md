# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpe.c

Ghostscript display driver for the Reflection Technology “Private Eye” display.

Key behavior:
- Defines `gx_device_pe`, extending `gx_device_common` with a framebuffer address and register base.
- Registers a device named `pe` with fixed geometry `720x280`, byte raster `90`, and default resolution `160x96`.
- Uses default framebuffer address `0xb8000000` and register base `0x3d0`, overrideable through `PEFBADDR` and `PEREGS` environment variables.
- `pe_open` parses environment overrides and writes initialization register/value pairs with `outportb`.
- `pe_close` writes restore register/value pairs and clears 4000 bytes of framebuffer memory.
- `pe_fill_rectangle` clips rectangles to the display, then sets or clears bits in the 1-bit framebuffer using first/last-byte masks.
- `pe_copy_mono` copies monochrome bitmap data into the framebuffer, handling aligned and skewed source/destination bit offsets, no-color behavior, inversion, and partial-byte masking.

Research notes:
- This is a hardware/display driver, not pdfwrite code and not filesystem code.
- It assumes direct port I/O and memory-mapped framebuffer access, so it is highly platform-specific.
