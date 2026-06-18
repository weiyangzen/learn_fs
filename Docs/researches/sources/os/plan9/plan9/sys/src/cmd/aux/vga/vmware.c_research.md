# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/vmware.c

VMware SVGA virtual video controller support.

Key behavior:
- Uses PCI device ID to select VMware register address/data ports:
  - `0x710`: fixed ports `0x4560/0x4564`.
  - `0x405`: BAR-derived ports.
- Reads VMware indexed registers into private `Vmware` state.
- Derives Plan 9 channel string from red/green/blue masks and host bits-per-pixel.
- Records framebuffer base and max size into `vga->vmb` and `vga->apz`.
- Validates SVGA version 2 by writing/reading `Rid`.
- Forces linear mode, clips requested dimensions to VMware max width/height, adopts VMware bpp, and updates `mode->chan`.
- Loads width/height, enables display, writes guest OS ID, and adjusts Plan 9 `vgactl size` if VMware bytes-per-line implies a wider virtual stride.
- Dumps all VMware registers plus channel/depth.

Integration:
- Exports `Ctlr vmware` and placeholder `Ctlr vmwarehwgc`.

Filesystem relevance:
- Indirect. It writes `/dev/vgactl` through `vgactlw()` when virtual stride changes.
