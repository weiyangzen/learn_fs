# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/nvidia.c

Plan 9 `aux/vga` controller for older NVIDIA/Riva/GeForce adapters. It detects NVIDIA PCI graphics devices, maps MMIO, classifies architecture generation, computes pixel PLL values, programs VGA CRTC extension registers, handles selected laptop/flat-panel state, initializes framebuffer memory limits, and seeds PFIFO/PGRAPH/PRAMIN acceleration objects.

Key behavior:
- `Nvidia` private state stores PCI identity, architecture class, crystal frequency, MMIO block pointers (`pfb`, `pramdac`, `pmc`, `ptimer`, `pfifo`, `pramin`, `pgraph`, `fifo`, `pcrtc`), saved CRTC extension registers, PLL fields, flat-panel fields, and head/dual-head flags.
- `snarf` chooses a PCI device from `vga->pci` or by matching NVIDIA vendor `0x10DE` and display class, maps `nvidiammio`, assigns sub-block pointers, resolves special PCI-X device IDs, classifies NV architecture 4/10/20/30/40 from device ID ranges, unlocks CRTC extensions, determines crystal frequency, dual-head and two-stage-PLL support, laptop LCD IDs, framebuffer size, saved VGA/NVIDIA registers, flat-panel dimensions, and controller state.
- `clock` searches valid M/N/P pixel PLL values based on crystal frequency, architecture, and one-stage versus two-stage PLL rules.
- `init` rejects 24-bit color, optionally forces LCD from mode attributes, computes cursor memory placement, VPLL/general state, blanking/overscan adjustments, overflow bits, pixel-depth fields, LCD scale bits, dual-head ownership, dither bits, and display height fields.
- `load` unlocks the chip, initializes PMC/PTIMER, writes memory-region registers, fills PRAMIN object tables for NV4x or older layouts, initializes PGRAPH based on architecture and device family, initializes PFIFO, writes head/cursor/LCD registers, writes CRTC extension registers, programs PLLs for CRT output or scale/sync registers for LCD output, and enables CRTC.
- `dump` reports computed PLL frequency and important NVIDIA state fields.

Notable dependencies:
- Plan 9 PCI helpers and VGA register helpers.
- `segattach` mapping named `nvidiammio`.
- Hardware constants are embedded directly in the source; this file does not include `riva_tbl.h` even though that header contains related NVIDIA initialization tables.

Research notes:
- The implementation covers a broad but old set of NVIDIA chips through hard-coded register offsets and device ID cases.
- Several register writes use array indexes that are already word-scaled in some blocks and byte-offset-divided in others; this is intentional in context but makes maintenance error-prone.
- If nForce special host-bridge lookup fails, `pcicfgr32(p, ...)` can be reached with `p == nil`.
- LCD support is partial and policy-heavy: many laptop IDs force `islcd`, and a mode attribute can override it.
- `nvidiahwgc` is a no-op descriptor; cursor setup lives inside the main mode-load path rather than a separate hardware-cursor controller.
