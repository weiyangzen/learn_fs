# File Research: sources/os/plan9/9front/sys/src/9/pc/vgavmware.c

VMware SVGA framebuffer and acceleration support for the Plan 9 VGA layer. It supports VMware PCI display devices, maps the framebuffer and FIFO MMIO area, and exposes update, copy, fill, and hardware cursor operations.

Key behavior:
- Identifies VMware PCI vendor/device IDs and selects either legacy fixed I/O ports or BAR-derived I/O ports depending on device generation.
- `vmwarelinear` computes framebuffer base from PCI BAR plus `Rfboffset`, maps the framebuffer, maps FIFO MMIO from BAR 2, initializes FIFO control words, and sets `Rconfigdone`.
- `vmfifowr` appends FIFO commands with wraparound and calls `vmwait` when the FIFO is full.
- `vmwareflush` emits `Xupdate` rectangles so VMware updates the visible display.
- Cursor support defines a 16x16 cursor through `Xdefinecursor`, builds AND/XOR masks from Plan 9 cursor data, and controls cursor position/visibility via SVGA registers.
- `vmwarescroll` emits `Xrectcopy`; `vmwarefill` emits `Xrectfill` for version 1 devices.
- `vgavmwaredev` installs linear mapping, draw initialization, and flush hooks; `vgavmwarecur` installs cursor hooks.

Notable dependencies:
- PCI discovery and BAR mapping.
- Port I/O helpers and VGA framebuffer registration.
- VMware SVGA register and FIFO command conventions embedded as local enums.

Research notes:
- The driver uses one global `Vmware` state object, so it is not structured for multiple simultaneous VMware VGA devices.
- FIFO waits are synchronous and busy-spin on `Rbusy`.
- Fill acceleration is deliberately limited to `vm->ver == 1`; scroll is enabled whenever MMIO is available.
