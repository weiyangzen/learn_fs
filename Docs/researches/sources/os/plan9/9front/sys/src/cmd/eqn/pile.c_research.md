# File Research: sources/os/plan9/9front/sys/src/cmd/eqn/pile.c

This file stacks boxes vertically for piles and matrix columns.

Key responsibilities:
- Reads pile metadata and member boxes from the global `lp` array.
- Computes inter-row gap from explicit separation, column type, or `Pilegap`.
- Computes total height and baseline based on the middle element.
- Measures maximum member width.
- Emits a troff string that vertically positions each member and aligns it left, right, or centered.
- Frees all member box registers.

Important implementation notes:
- Column types `LCOL`, `RCOL`, `CCOL`, and `COL` select horizontal alignment.
- Even-length piles use `Pilebase` for baseline placement.
- The final box clears left/right font metadata.
