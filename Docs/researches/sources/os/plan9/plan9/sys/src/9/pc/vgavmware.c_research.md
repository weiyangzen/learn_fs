# File Research: sources/os/plan9/plan9/sys/src/9/pc/vgavmware.c

## Purpose
VMware SVGA VGA driver providing linear framebuffer mapping, FIFO update commands, rectangle fill/copy acceleration, and hardware cursor support.

## Main Interfaces
- Exports `VGAdev vgavmwaredev` named `vmware`.
- Exports `VGAcur vgavmwarecur` named `vmwarehwgc`.
- Installs `scr->scroll`, `scr->fill`, and `flush` callbacks.

## Implementation Notes
- Probes PCI vendor `0x15AD` and supports device IDs `0x0710` and `0x0405`.
- Register access is via VMware index/data I/O ports, either fixed `0x4560` or from PCI BAR 0.
- `vmwarelinear` maps `Rfbstart` with twice `Rfbsize`, matching an empirical comment about larger modes.
- `vmwaredrawinit` maps FIFO MMIO from `Rmemstart/Rmemsize`, initializes FIFO control words, writes `Rconfigdone`, and adjusts screen data by `Rfboffset`.
- FIFO commands implement update, rectcopy, rectfill, and cursor definition/display/move.
- Cursor conversion builds 16-line AND/XOR masks from Plan 9 cursor bitplanes.

## Dependencies And Risks
- Global singleton `vm` means only one VMware VGA instance is represented.
- FIFO writer busy-waits via sync when space is exhausted.
- `vmwareblank` is a no-op, so display blanking is not implemented.
