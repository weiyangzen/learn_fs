# File Research: sources/os/plan9/9front/sys/src/cmd/eqn/fromto.c

This file renders lower and upper limits attached to a base box, used for constructs like `sum from ... to ...`.

Key responsibilities:
- Allocates a new result register.
- Measures base, lower, and upper boxes with `nrwid`.
- Computes the maximum width needed to center all components.
- Stacks lower limit below, base in the middle, and upper limit above using vertical and horizontal troff escapes.
- Updates height and baseline for the combined result.
- Frees consumed component registers.

Important implementation notes:
- The lower limit contributes to the baseline offset.
- `ps` is adjusted via `deltaps` to render limits at a smaller size.
- Missing lower or upper boxes are handled independently.
