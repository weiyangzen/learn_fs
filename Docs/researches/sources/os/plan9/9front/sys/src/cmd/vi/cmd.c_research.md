# File Research: sources/os/plan9/9front/sys/src/cmd/vi/cmd.c

`cmd.c` is the interactive debugger command loop for `vi`, an adb-like MIPS simulator. It parses expressions, counts, commands, formatting modifiers, breakpoints, run/continue/step commands, stack/register/stat commands, memory inspection, expression evaluation, and register assignment.

Supported commands include `:b`, `:d`, `:r`, `:c`, `:s`, `$r`, `$f`, `$F`, `$b`, `$c`, `$C`, trace toggles, instruction summaries, and memory display via `?`/`/`. `pfmt()` implements numeric, character, string, instruction, symbol, source, and global formats.

The command loop uses `setjmp(errjmp)` recovery and a note handler for interrupts. It is the operator-facing shell over the simulator core.
