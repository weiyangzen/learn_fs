# File Research: sources/os/plan9/9front/sys/src/cmd/kl/list.c

Formatting and diagnostics support for the SPARC linker. It installs `Fmt` converters, prints assembly instructions, formats opcodes, addresses, branch targets, symbolic offsets, and string constants, and emits linker diagnostics with current text symbol context.

Compared with the compiler formatter, linker `Dconv` understands linker-resolved branch targets through `curp->cond`, P registers, ASI operands, and floating constants stored as split IEEE words. `diag` increments global error count and exits after too many errors. This file supports debug listings and human-readable error messages throughout `kl`.
