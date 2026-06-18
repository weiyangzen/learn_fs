# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/radeon.h

Large Radeon register-definition header used by `radeon.c`. It is adapted from ATI/XFree86-era Radeon/Rage128 material and contains MMIO offsets, PLL offsets, bit masks, packet constants, and supported PCI IDs.

Key contents:
- Copyright/license notice and a warning that the file was converted from `r128_reg.h` and may contain definitions not correct for Radeon without a full audit.
- BIOS access macros `BIOS8`, `BIOS16`, `BIOS32` and `BIOS_START`.
- Register offsets and bit fields for PCI config aliases, AGP, VGA attribute/graphics/sequence registers, BIOS scratch registers, brush/2D engine registers, bus control, clock/PLL access, color compare, CRTC1/CRTC2 timing and cursor registers, DAC registers, GPIO/DDC, overlays, flat-panel/LVDS/TMDS controls, memory controller, RBBM/reset/status, 2D destination cache, scissor/source/destination registers, surface registers, wait/idle controls, 3D/texture/render backend/TCL registers, command processor registers, and CP packet formats.
- Constants for AGP texture offset, scratch registers, CP packet type construction, vertex format/control fields, and shader/light/material address slots.
- ATI vendor ID, `struct pciids`, Radeon family enum values, and `radeon_pciids[]` entries for Mobility M7/M9, RV100/R100/R200/RV200/RV250, and R300 device IDs.

Notable dependencies:
- Intended to be included in C files that already define Plan 9 types such as `uchar`, `ushort`, and `ulong`.
- `struct pciids` and `radeon_pciids[]` are concrete definitions, so this header should not be included by multiple translation units without care.

Research notes:
- Many definitions are unused by the local `radeon.c`, which uses mainly BIOS macros, CRTC/DAC/PLL/common register constants, and PCI ID data.
- There is a suspicious mask definition: `R300_PPLL_REF_DIV_ACC_MASK` is written as `(0x3ff < 18)` rather than a left shift. That expression evaluates as a comparison, not the intended bit mask, and affects R300 PLL handling in `radeon.c`.
- Because this is a direct hardware-definition header with embedded data, validation risk is about register correctness rather than control flow.
