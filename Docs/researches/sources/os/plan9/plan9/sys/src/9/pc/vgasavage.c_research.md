# File Research: sources/os/plan9/plan9/sys/src/9/pc/vgasavage.c

S3 Savage acceleration helper used by `vgas3.c` via external `savageinit(VGAscr*)`. It does not export a `VGAdev`; it initializes fill, scroll, and blank callbacks for supported Savage chips.

The file documents difficulty with Savage BCI and chooses packed new MMIO registers. It defines extensive 2D engine, status, FIFO, command, mix, bitmap descriptor, and alternate status registers for Savage4-like hardware.

Runtime behavior:
- `savagewaitidle()` chooses status register/mask based on chip ID, waiting for engine idle and FIFO empty; timeout snapshots are stored in `savagestats`.
- `savagefill()` programs foreground/background color, mix mode, rectangle coordinates, size, and fill command.
- `savagescroll()` programs source/destination coordinates, direction bits, mix mode, and bitblt command.
- `savageblank()` controls DPMS sync bits and LCD enable through sequencer registers.
- `savageinit()` validates chip ID, resets the 2D engine, disables BCI, enables 32-bit writes and no clipping, enables planes, turns on linear access/2D engine, sets global/primary/secondary bitmap descriptors, and installs `scr->fill`, `scr->scroll`, and `scr->blank`.

Supported IDs include Savage4, ProSavage variants, SavageIX/MX mobile variants, and SuperSavageIXC16. Unknown IDs print a warning and leave acceleration unset.
