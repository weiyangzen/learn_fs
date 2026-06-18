# File Research: sources/os/plan9/plan9/sys/src/9/pc/vgaet4000.c

Tseng ET4000 bank-switch and hardware sprite cursor support. `setet4000page()` programs page bits via ports `0x3CD` and `0x3CB`; `et4000page()` wraps it with `scr->devlock`.

Cursor behavior:
- `et4000enable()` configures CRTCB/Sprite registers through indexed ports `0x217A/0x217B`, selects 64x64 sprite mode, computes 1024-byte-aligned storage after visible framebuffer, configures row offset/depth, and enables sprite display.
- `et4000load()` locks display memory, disables cursor, banks to cursor storage, writes a 64x64 two-plane sprite image, and re-enables.
- `et4000move()` waits for vertical status to avoid jerky cursor updates, handles negative coordinates through preset registers, then writes X/Y position.
- Comments warn the cursor color conversion is likely stale for third-edition color values.

Exports `VGAcur vgaet4000cur` and `VGAdev vgaet4000dev`.
