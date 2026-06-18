# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/tvp3026clock.c

Computes TVP3026 pixel and loop clock PLL parameters.

Key responsibilities:
- Selects VGA standard clocks or external programmable-clock selection bits in `vga->misc`.
- Brute-force searches TVP3026 PCLK parameters `m`, `n`, and `p` under VCO constraints.
- Computes loop clock fields using enhanced-mode dependent factor `k`.
- Stores PCLK in `vga->m[0]`, `vga->n[0]`, `vga->p[0]`.
- Stores loop clock in `vga->m[1]`, `vga->n[1]`, `vga->p[1]`, `vga->q[1]`, and `vga->f[1]`.

Important interfaces:
- Exports `Ctlr tvp3026clock`.
- Provides only an `init` function.

Notes:
- Uses scaled arithmetic (`SCALE(f) ((f)/10)`) to reduce overflow risk in brute-force search.
