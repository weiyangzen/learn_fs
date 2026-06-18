# File Research: sources/os/plan9/plan9/sys/src/9/pc/vgacyber938x.c

Trident Cyber938x page, linear framebuffer, MMIO discovery, and hardware cursor support. `cyber938xpage()` banks through ports `0x3D8/0x3D9`. `cyber938xlinear()` uses PCI vendor `0x1023`, maps the framebuffer, heuristically maps BAR1 as 128KB MMIO when present, and exports screen/MMIO segments.

Cursor support uses CRTC registers:
- `0x50` controls cursor mode/enable.
- `0x44/0x45` store cursor base.
- `0x40` through `0x47` store position and origin.
- `0x48` through `0x4F` store colors.

`cyber938xcurload()` supports banked or linear cursor storage, writes a 32x32 image, stores hotpoint offset, and enables cursor mode `0xC8`. `cyber938xcurmove()` handles negative coordinates via origin registers.

Exports `VGAdev vgacyber938xdev` and `VGAcur vgacyber938xcur`.
