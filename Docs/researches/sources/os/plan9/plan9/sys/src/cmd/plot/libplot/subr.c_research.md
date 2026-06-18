# File Research: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/subr.c

Global libplot environment state and color parsing.

Key responsibilities:
- Defines the `E[9]` environment stack and pointers `e0`, `e1`, `esave`.
- Parses color/style strings through `bcolor()`.
- Copies plotting environments with `sscpy()`.
- Provides stub `idle()` and `ptype()`.

Important behavior:
- Numeric color strings are mapped through `cmap2rgba()`.
- Letter colors map to Plan 9 draw constants: black, red, green, blue, magenta, yellow, cyan, white.
- `R` returns a raw integer color.
- `G` and `A` set pen gap/slant side effects and return `-1`.

Notable risks:
- `E` is initialized with eight explicit elements despite size nine; the last is zero-initialized.
- `sscpy()` does not copy `pgap` or `pslant`, so some side-effect state is not saved/restored.
- `bcolor()` has implicit `int` return style.
