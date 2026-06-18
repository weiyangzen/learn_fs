# File Research: sources/os/plan9/9front/sys/src/cmd/vi/symbols.c

`symbols.c` provides source and stack-symbol display for the `vi` debugger. It maps PCs to `file:line`, prints local auto variables and parameters from symbol metadata, and implements stack traces with optional locals.

`stktrace()` follows frames using `.frame` symbols, saved PC, stack pointer, and return register logic until `_main` or a truncation limit. It prints called-from information with symbol offsets and source lines.

This file depends on Plan 9 `mach` symbol APIs and simulated memory reads for stack frame values.
