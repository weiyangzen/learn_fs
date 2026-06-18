# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/tvp3025clock.c

Computes TVP3025 pixel clock PLL parameters.

Key responsibilities:
- If needed, initializes `vga->f[0]` from the display mode frequency.
- Brute-force searches divider `d`, multiplier `n`, and post-divider `p`.
- Enforces documented constraints for reference divider and VCO range.
- Stores the best parameters in `vga->d[0]`, `vga->n[0]`, and `vga->p[0]`.

Important interfaces:
- Exports `Ctlr tvp3025clock`.
- Provides only an `init` function; no direct load/dump phase.

Notes:
- The actual DAC programming is performed elsewhere; this file only calculates shared clock fields.
