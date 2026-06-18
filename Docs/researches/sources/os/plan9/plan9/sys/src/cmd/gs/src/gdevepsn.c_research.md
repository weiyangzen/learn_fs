# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevepsn.c

Monochrome Epson/IBM dot-matrix printer family driver.

Key behavior:
- Defines `epson`, `eps9mid`, `eps9high`, and `ibmpro`.
- Shared `eps_print_page` handles printer initialization, scanline copying, vertical skipping, 8x8 transposition, horizontal tab compression, and double-density even/odd passes.
- Special 9-pin modes interleave or merge vertical lines for higher apparent resolution.
- IBM ProPrinter path uses different initialization and archaic behavior.

Risks / notes:
- Assumes specific legal DPI combinations but mostly trusts configured values.
- Many printer quirks are compile-time macros.
