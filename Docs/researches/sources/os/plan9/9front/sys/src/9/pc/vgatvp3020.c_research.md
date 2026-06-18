# File Research: sources/os/plan9/9front/sys/src/9/pc/vgatvp3020.c

Hardware cursor support for the TI TVP3020 Viewpoint video palette, assumed to be attached to an S3 86C928 VGA controller.

Key behavior:
- Uses CRTC register `0x55` to select the upper indirect DAC address bits, then uses standard VGA palette ports for TVP3020 indexed register access.
- `tvp3020disable` clears cursor enable, Bt485-compatible cursor control, and S3 external hardware cursor mode bits.
- `tvp3020enable` initializes cursor control, sets overscan and cursor colors, and enables the S3 external cursor path.
- `tvp3020load` writes the Plan 9 16x16 cursor into a 64x64 hardware cursor RAM area, padding the rest with transparent pixels.
- `tvp3020move` updates low/high cursor X/Y position registers.

Notable dependencies:
- VGA indexed I/O helpers `vgaxi`, `vgaxo`, `vgao`.
- VGA palette register constants and `Cursor` masks from the PC screen subsystem.

Research notes:
- The cursor data conversion is explicit and bit-order-sensitive: each byte encodes four 2-bit cursor pixels.
- The driver only exports `VGAcur vgatvp3020cur`; it does not provide a full `VGAdev` framebuffer or mode-setting driver.
