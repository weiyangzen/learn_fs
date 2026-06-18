# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/hiqvideo.c

Implements Chips & Technologies HiQVideo/HiQV32 PCI controller setup for devices including 69000 and 65550/65554/65555. It snarfs flat-panel, multimedia, configuration, and CRTC extension registers and determines max clock/memory size from PCI ID, voltage, and extension state.

The clock routine brute-forces PLL `M/N`, post divisor, and reference divisor under HiQVideo constraints. `init` supports 8/16/32 bpp, avoids DCLK programming for LCD output, handles standard VGA clocks specially, computes extended CRTC overflow fields, sets color-depth registers, and enables linear aperture when requested.

`load` synchronizes with vertical retrace, programs PLL registers when needed, writes extended CRTC/XR/FR state, and sets linear base registers. `dump` decodes VCLK and MCLK values.
