# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/tvp3025clock.c

TVP3025 PLL parameter calculator.

Key behavior:
- Computes `vga->d[0]`, `vga->n[0]`, and `vga->p[0]` for the desired pixel clock.
- Brute-force searches D/N/P values for:
  - `Fvco = RefFreq*((n+2)*8)/(d+2)`
  - `Fpll = Fvco / 2**p`
- Enforces approximate VCO range 110-220 MHz and reference-divider constraints.
- Sets default PLL fields before search and marks `Finit`.

Integration:
- Does not load registers itself; `s3clock.c` uses these fields in `tvp3025load()`.

Filesystem relevance:
- Indirect display clock calculation.
