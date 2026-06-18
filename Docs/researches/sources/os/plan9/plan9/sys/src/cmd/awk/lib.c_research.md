# File Research: sources/os/plan9/plan9/sys/src/cmd/awk/lib.c

Runtime support for records, fields, command-line files, and diagnostics.

Main responsibilities:

- Allocates `$0`/field cells with `recinit()`, `makefields()`, and `growfldtab()`.
- Traverses `ARGV`, applies command-line `var=value`, opens input files, tracks `FILENAME`, `NR`, and `FNR`.
- Reads records with `RS`, including paragraph mode when `RS` is empty.
- Splits fields using default whitespace, single-character `FS`, empty `FS`, or regex `FS`.
- Rebuilds `$0` from fields and `OFS` when fields change.
- Invalidates field/record caches via `donefld` and `donerec`.

Diagnostics include `SYNTAX`, `FATAL`, `WARNING`, brace checking, source/input context reporting, floating-point exception handling, and numeric-string detection via `strtod()`.
