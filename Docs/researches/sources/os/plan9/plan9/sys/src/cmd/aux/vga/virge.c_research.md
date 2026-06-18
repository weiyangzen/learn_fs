# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/virge.c

S3 Trio64+/ViRGE/Savage/ProSavage controller support.

Key behavior:
- Unlocks and reads extended sequencer/CRTC registers, then identifies chip variant by `Crt2D:Crt2E`.
- Handles IDs for Trio64+, Aurora64V+, Trio64V2, ViRGE, ViRGE/DX/GX, ViRGE/GX2, ViRGE/VX, Savage MX/MV, Savage4/IX, SuperSavage/IXC16, Savage4, ProSavage PN133/KN133/DDR.
- Sets PLL limits, memory sizes, and aperture sizes per chipset.
- Rounds virtual width to a multiple of 16 for Savage-family chips.
- Configures mode-specific CRTC/sequencer state for depth, byte width, FIFO, MMIO method, clocking, and color mode.
- Uses `trio64clock()` for PLL calculation, with variant-specific packing of M/N/R high bits.
- Supports `noclockset` mode attribute to avoid programming clocks.
- Loads generic S3 state, PLL registers, variant-specific registers, and advanced-function control when needed.
- Dumps extended CRTC/sequencer ranges and decodes DCLK/MCLK.

Important details:
- Comments mark some Savage/SuperSavage values as guessed or hardware-derived.
- Supports 8/15/16/24/32 bpp depending on variant; some unsupported depths error.

Filesystem relevance:
- Indirect display controller code.
