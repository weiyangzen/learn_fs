# File Research: sources/os/plan9/9front/sys/src/cmd/eqn/over.c

This file implements fractions with the `over` operator.

Key responsibilities:
- Measures numerator and denominator widths.
- Chooses the maximum width plus extra rule width.
- Places denominator below and numerator above the fraction bar.
- Emits a horizontal rule between them.
- Updates combined height and baseline.
- Frees the denominator and temporary width register.

Important implementation notes:
- Tuning parameters `Overgap`, `Overwid`, and `Overline` control spacing and bar length.
- The numerator register is reused as the final result.
- Both left and right font metadata are cleared because the result is a composed object.
