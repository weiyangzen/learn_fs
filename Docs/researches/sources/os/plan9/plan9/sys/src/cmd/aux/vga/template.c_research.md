# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/template.c

Skeleton controller template for `aux/vga` modules.

Key behavior:
- Includes no real hardware behavior.
- Defines stub `snarf`, `options`, `init`, `load`, and `dump` callbacks.
- Each stub marks the corresponding controller flag except `dump`, which only consumes arguments.
- Exports `Ctlr xxx`.

Use:
- Serves as a copy/edit template for new VGA controller modules.

Filesystem relevance:
- None beyond being source scaffolding.
