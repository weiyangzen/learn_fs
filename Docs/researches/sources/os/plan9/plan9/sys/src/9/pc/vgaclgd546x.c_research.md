# File Research: sources/os/plan9/plan9/sys/src/9/pc/vgaclgd546x.c

Cirrus Logic CL-GD546x PCI/MMIO and hardware cursor support. It matches PCI vendor `0x1013` device IDs `0xD0`, `0xD4`, and `0xD6`, maps BAR1 MMIO, exports `clgd546xmmio`, and uses `vgalinearpci()` for the framebuffer.

Cursor support maps a `Cursor546x` register block at MMIO offset `0xE0`. It disables through the `enable` field, writes bit-reversed 64x64 cursor data to framebuffer storage, sets palette cursor colors via `PaletteState`, computes storage from sequencer register `0x14`, initializes two cursor images, and moves via `preset`, `x`, and `y` fields.

Exports `VGAdev vgaclgd546xdev` and `VGAcur vgaclgd546xcur`.
