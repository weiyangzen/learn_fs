# File Research: sources/os/plan9/plan9/sys/src/9/pc/vganeomagic.c

NeoMagic MagicGraph/MagicMedia VGA driver with linear framebuffer, hardware cursor, and 2D acceleration.

Key responsibilities:
- Detects supported NeoMagic PCI IDs and selects cursor-register offset, video-memory size, and MMIO BAR/offset.
- Maps MMIO, registers `neomagicmmio`, maps linear framebuffer, and registers `neomagicscreen`.
- Places two 1 KiB cursor images at the end of video memory.
- Implements 64x64 cursor image generation, negative-position shifted image generation, and cursor register programming.
- Initializes NeoMagic blitter state and exports hardware fill/scroll for supported depths and widths.

Important behavior:
- Older 128ZV uses an MMIO region offset from BAR0; later devices use BAR1.
- Cursor address bits are rearranged before writing the cursor address register.
- Blitter mode depends on screen depth and width; 24 bpp is explicitly not supported for acceleration.
- Fill and scroll use MMIO blit registers with busy/FIFO polling.

Exports:
- `VGAdev vganeomagicdev` named `neomagic`.
- `VGAcur vganeomagiccur` named `neomagichwgc`.

Notable risks:
- Comments note MMIO layout may differ for older chips.
- `waitforidle` and `waitforfifo` timeout diagnostics are commented out, so hangs can be quiet.
- 24 bpp acceleration is intentionally disabled.
