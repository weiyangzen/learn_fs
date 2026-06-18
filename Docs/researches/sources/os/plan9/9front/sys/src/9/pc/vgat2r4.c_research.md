# File Research: sources/os/plan9/9front/sys/src/9/pc/vgat2r4.c

Plan 9 VGA driver support for the Number Nine Ticket to Ride IV controller. It maps the device MMIO BAR, exposes framebuffer/MMIO VGA segments, implements hardware cursor support, and hooks accelerated rectangle fill/scroll operations into `VGAscr`.

Key behavior:
- `t2r4enable` maps PCI BAR 4 as MMIO, records `scr->mmio`, calls `vgalinearpci`, and exports `t2r4mmio` / `t2r4screen` VGA segments.
- Indexed register helpers `t2r4xi` and `t2r4xo` write low/high index registers then read/write the indexed data register.
- Cursor support programs cursor RAM, cursor colors, hot spot, position, and sync/enable bits. The cursor is translated from Plan 9 `Cursor` masks into the card’s 2-bit-per-pixel cursor format.
- Drawing acceleration initializes destination/source pitch and format for `RGB15`, `RGB16`, and `XRGB32`, then installs `scr->fill`, `scr->scroll`, and `scr->blank`.
- `t2r4hwscroll` emits a bitblt with direction control for overlapping source/destination rectangles, with explicit bailouts for small horizontal copies on known problematic SGI flat panel setups.
- `t2r4hwfill` emits a foreground-color bitblt fill, and `t2r4blank` manipulates cursor/sync control bits to force sync-low blanking.

Notable dependencies:
- Plan 9 PC kernel VGA infrastructure: `screen.h`, `VGAscr`, `VGAdev`, `VGAcur`, `vgalinearpci`, `addvgaseg`.
- PCI and VM mapping helpers: `Pcidev`, `vmap`.
- Draw cursor types and pixel channel constants.

Research notes:
- The file is self-contained hardware register programming; it assumes `scr->pci` is already matched to the target device.
- Busy waits have fixed million-iteration cutoffs and only print diagnostic messages on timeout; callers still continue after timeout.
- Hardware acceleration is disabled for unsupported color channels by clearing `scr->fill` and `scr->scroll`.
