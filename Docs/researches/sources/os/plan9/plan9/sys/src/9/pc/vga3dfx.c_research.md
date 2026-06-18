# File Research: sources/os/plan9/plan9/sys/src/9/pc/vga3dfx.c

3dfx Banshee/Voodoo3 VGA device and hardware cursor support. `tdfxenable()` matches PCI vendor `0x121A` devices `0x0003` and `0x0005`, maps MMIO BAR0, exports `3dfxmmio`, enables linear framebuffer mapping, exports `3dfxscreen`, and computes cursor storage at the last 1KB of display memory based on DRAM/SGRAM strap registers.

Cursor support uses the `Cursor3dfx` MMIO block at `hwCur`. It disables/enables the cursor through `vidProcCfg`, uploads a 64x64 X11-format cursor into framebuffer storage, sets black/white cursor colors, stores the hardware-specific hotpoint offset, and moves by writing `hwCurLoc`.

Exports:
- `VGAdev vga3dfxdev` with enable only.
- `VGAcur vga3dfxcur` named `"3dfxhwgc"` with enable/disable/load/move.
