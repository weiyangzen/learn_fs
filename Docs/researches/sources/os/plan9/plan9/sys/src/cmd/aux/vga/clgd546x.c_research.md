# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/clgd546x.c

Controller backend for Cirrus Logic Laguna CL-GD546x visual media accelerators.

Core behavior:
- Locates PCI vendor `0x1013`, device `0xD0`, `0xD4`, or `0xD6`.
- Sets kernel VGA type to `clgd546x`.
- Attaches `clgd546xmmio` segment for MMIO register access.
- Saves standard extended VGA registers and Laguna MMIO registers.
- Uses PCI BAR 0 size for video memory and advertises linear framebuffer.
- Reuses `clgd54xxclock()` for VCLK.
- Programs format, display threshold, tiling control, vendor-specific control, 2D control, and tiling control for 2D/3D.

Ctlrs:
- `clgd546x`
- `clgd546xhwgc` placeholder.

Notable risks:
- Although format logic has cases for 16/24/32, the file rejects `mode->z > 8`, so high-depth code is unreachable.
- Tiling/interleave controls are simplified with `nointerleave` and `notile` forced on.
