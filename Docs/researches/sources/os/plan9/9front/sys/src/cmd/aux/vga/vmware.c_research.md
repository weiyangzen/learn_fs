# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/vmware.c

Implements VMware SVGA controller support.

Key responsibilities:
- Detects VMware video PCI device IDs `0x0710` and `0x0405`.
- Sets register address/data ports based on VMware SVGA version.
- Reads VMware SVGA register set into private `Vmware` state.
- Derives Plan 9 channel string from red/green/blue masks and host depth/bpp.
- Sets framebuffer base and aperture size from PCI BARs/registers.
- Validates VMware SVGA version 2, clips requested screen size to max dimensions, and forces mode depth/channel to device values.
- Programs width/height/enable/guest ID during load.
- Updates `/dev/vgactl` size when device stride differs from visible width.

Important interfaces:
- Exports `Ctlr vmware` and stub `Ctlr vmwarehwgc`.
- Uses `vgactlpci`, `vgactlw`, `outportl`, `inportl`.

Notes:
- The clock routine is intentionally empty.
- Uses linear/enhanced mode unconditionally after initialization.
