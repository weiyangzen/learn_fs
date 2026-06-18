# File Research: sources/os/plan9/plan9/sys/src/9/pc/vgat2r4.c

## Purpose
Driver support for the Number Nine Ticket to Ride IV VGA device, covering PCI/MMIO discovery, hardware cursor programming, accelerated rectangle fill/scroll, and display blanking.

## Main Interfaces
- Exports `VGAdev vgat2r4dev` named `t2r4`.
- Exports `VGAcur vgat2r4cur` named `t2r4hwgc`.
- Installs `scr->fill`, `scr->scroll`, and `scr->blank` during `t2r4drawinit`.
- Uses `scr->mmio`, `scr->pci`, `scr->gscreen`, `scr->paddr`, and `scr->apsize`.

## Implementation Notes
- `t2r4enable` locates PCI vendor `0x105D`, device `0x5348`, maps BAR 4, registers VGA segments, and calls `vgalinearpci`.
- Cursor register access is indirect through MMIO `IndexLo`, `IndexHi`, and `Data`.
- Cursor image conversion maps Plan 9 `Cursor` `clr`/`set` bitplanes into the device cursor RAM truth table.
- Hardware acceleration writes command-engine registers under `RBaseD`, with bounded polling in `waitforfifo`, `waitforcmd`, and `waitformem`.
- `t2r4drawinit` supports `RGB15`, `RGB16`, and `XRGB32`; unsupported channels disable acceleration callbacks.

## Dependencies And Risks
- Depends on Plan 9 VGA core structures from `screen.h`, PCI helpers, `vmap`, and low-level MMIO ordering.
- Hardware polling uses fixed spin limits and only logs timeout symptoms.
- Scroll has explicit small-horizontal-scroll workarounds for SGI flat panels.
- Cursor Y coordinates and hotspots are scaled by the device zoom register.
