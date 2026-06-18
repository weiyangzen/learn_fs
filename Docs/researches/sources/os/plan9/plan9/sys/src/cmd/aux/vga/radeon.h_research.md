# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/radeon.h

Provides Radeon register definitions, bit masks, BIOS helpers, command processor constants, and supported ATI PCI IDs for `radeon.c`.

Key contents:
- `BIOS8`, `BIOS16`, and `BIOS32` macros plus `BIOS_START`.
- Register offsets and masks for PCI config, AGP, VGA compatibility, BIOS scratch, bus control, memory configuration, CRTC/CRTC2, DAC, cursor, flat-panel/LVDS, GPIO/DDC, overlay/video scaler, palette, PLL, surface, interrupt, and wait/flush control.
- 2D engine constants for brush, destination/source coordinates, pitches, Bresenham line state, ROP3, clipping, host data, and GUI master control.
- 3D/TCL constants for pixel pipeline, texture formats/blends, cube maps, render backend, stencil/depth, setup engine, viewport, lighting, matrices, vertex formats, and material/light state.
- Command processor and microcode registers, CP packet type definitions, packet-3 opcodes, vertex control format masks, and shader/light address constants.
- `ATI_PCIVID`, `struct pciids`, Radeon family enum values, and `radeon_pciids[]` mapping device IDs to R100/R200/R300/mobile families.

Important details:
- Header comments warn it was converted from `r128_reg.h` and contains unaudited definitions that may be incorrect for Radeon.
- The R300 `R300_PPLL_REF_DIV_ACC_MASK` macro uses `(0x3ff < 18)`, which reads as a suspicious comparison rather than a shift.
- Many constants are unused by `radeon.c` but likely copied for future acceleration or broader driver use.
- The PCI ID table terminates with a zero `did`.

Filesystem relevance:
- Indirect: register definition support for the Radeon video backend, not filesystem behavior.
