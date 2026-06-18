# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/template.c

Provides a skeleton `aux/vga` controller implementation.

Key responsibilities:
- Shows the expected `snarf`, `options`, `init`, `load`, and `dump` function shape.
- Marks phase-completion flags `Fsnarf`, `Foptions`, `Finit`, and `Fload`.
- Exports a placeholder `Ctlr xxx`.

Important interfaces:
- Uses `USED` macros to silence unused-parameter warnings.

Notes:
- This is not a functional hardware driver; it is a source template for adding new VGA controllers.
