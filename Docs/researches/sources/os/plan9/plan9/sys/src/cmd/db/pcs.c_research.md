# File Research: sources/os/plan9/plan9/sys/src/cmd/db/pcs.c

This file implements the debugger’s `:` subprocess-control command dispatcher.

Key behaviors:
- `subpcs(int modif)` handles breakpoint control, process execution, single stepping, continuing, killing, note management, and stopping/resuming an attached process.
- `:b`/`:B` set normal or temporary breakpoints at `dot`, optionally reading a command string to execute at the breakpoint.
- `:d`/`:D` clear a breakpoint at `dot`.
- `:r`/`:R` restarts the debugged program via `endpcs()`, `setup()`, and `runpcs(CONTIN, ...)`.
- `:s` single-steps; `:S` single-steps until source-line changes, using `pc2line()`.
- `:c`/`:C` continue a running process.
- `:n` lists or deletes pending notes.
- `:h` grabs/stops a current process or ungrabs it when address `0` is supplied.
- `:x` resumes an already grabbed process.

Notable implementation details:
- Breakpoint commands default to an effectively infinite count when no explicit count is given and the command is non-empty.
- On command completion it removes installed breakpoints with `delbp()`, prints the current PC, and displays pending notes.
- It depends on globals from process-control code: `pid`, `nnote`, `note`, `pcsactive`, `loopcnt`, and breakpoint list state.
