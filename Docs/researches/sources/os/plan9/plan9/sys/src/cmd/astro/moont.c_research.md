# File Research: sources/os/plan9/plan9/sys/src/cmd/astro/moont.c

Lunar perturbation coefficient table.

Key points:
- Defines `moontab[]`, a sequence of coefficient and integer multiplier records.
- The table is divided into zero-terminated sections consumed by `moon.c` for longitude, latitude sine terms, latitude cosine terms, node terms, and parallax terms.

Dependencies:
- Data format is coupled to `Moontab` and `moon.c`’s sequential section parsing.

Notable behavior:
- Contains no control logic; the zero rows delimit subseries.
