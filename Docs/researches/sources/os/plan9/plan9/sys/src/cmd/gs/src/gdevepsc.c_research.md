# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevepsc.c

Color Epson dot-matrix printer driver, primarily for LQ-2550-style color output.

Key behavior:
- Defines `epsonc` printer device.
- Maps RGB to 8 Epson ribbon colors, with violet mapped to blue on reverse conversion.
- Converts scanline bands into Epson graphics commands.
- Handles 9-pin/24-pin modes, double-density passes, vertical skipping, tabbing, and color passes.
- Transposes 8x8 raster blocks into printer pin order.

Risks / notes:
- Compile-time `X_DPI`/`Y_DPI` combinations are not fully validated.
- Complex color-pass logic mutates the color buffer while extracting per-color mono passes.
