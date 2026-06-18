# File Research: sources/os/plan9/plan9/sys/src/9/pc/vgaclgd542x.c

Cirrus Logic CL-GD542x/543x/544x/7543/5480 page, linear, and hardware cursor support. `clgd542xpageset()` handles bank selection using graphics registers `0x09`/`0x0B`, with special handling when sequencer `0x07` indicates linear mode. `clgd542xlinear()` uses PCI vendor `0x1013`.

Cursor behavior:
- `clgd542xenable()` disables the cursor, programs DAC colors, detects approximate memory size from chip ID and sequencer registers, chooses storage in the last 16KB, selects cursor index 0, and enables a 64x64 cursor.
- `clgd542xinitcursor()` writes cursor image data, optionally shifted for offscreen-left/top clipping, using either banked or linear access.
- `clgd542xload()` saves the cursor into `scr->Cursor`, initializes cursor image 0, and re-enables.
- `clgd542xmove()` handles negative coordinates by generating shifted cursor image 1 and selecting it.

Exports `VGAdev vgaclgd542xdev` and `VGAcur vgaclgd542xcur`.
