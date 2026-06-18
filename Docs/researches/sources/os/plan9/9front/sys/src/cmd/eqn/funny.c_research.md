# File Research: sources/os/plan9/9front/sys/src/cmd/eqn/funny.c

This file creates special large operator boxes for sum, product, union, and intersection.

Key responsibilities:
- Maps parser tokens (`SUM`, `PROD`, `UNION`, `INTER`) to predefined troff strings in `deftbl`.
- Allocates a new box register.
- Sets height and baseline using tuning parameters `Funnyps`, `Funnyht`, and `Funnybase`.
- Marks the box as roman on both sides.

Important implementation notes:
- Unknown operator types are fatal.
- The actual glyph definitions are installed by `tuning.c` (`sum_def`, `prod_def`, `union_def`, `inter_def`).
