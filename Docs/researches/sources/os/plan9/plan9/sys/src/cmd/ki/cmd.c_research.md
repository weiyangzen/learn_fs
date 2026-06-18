# File Research: sources/os/plan9/plan9/sys/src/cmd/ki/cmd.c

This file implements the interactive debugger command language for `ki`. It is adb-like, with address expressions, repeat counts, format modifiers, run/step/continue commands, register display, stack traces, and breakpoint control.

Expression handling resolves symbols, `.` current address, hex literals with `#`, numeric literals, and simple binary operators. `colon()` implements run/continue/step and breakpoint commands. `dollar()` implements register dumps, stack traces, breakpoint listing, tracing flags, summaries, profiling, and quit.

`pfmt()` formats memory or expression values as octal, decimal, hex, bytes/chars/strings, addresses, globals, disassembly, and source lines. `quesie()` prints memory with repeat counts and line wrapping. `setreg()` writes emulated registers.

`cmd()` runs the read-evaluate loop, stores the last command for blank-line repeat, handles interrupts through `notify()`, and uses `setjmp(errjmp)` as the debugger recovery boundary.
