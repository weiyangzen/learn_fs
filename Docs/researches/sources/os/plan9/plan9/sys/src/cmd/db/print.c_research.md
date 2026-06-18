# File Research: sources/os/plan9/plan9/sys/src/cmd/db/print.c

This file implements the debugger’s `$` command family and general debugger inspection output.

Key behaviors:
- `printtrace(int modif)` dispatches `$` commands:
  - `$<`, `$<<` redirect input from command files.
  - `$>` redirects output.
  - `$a` attaches to a process.
  - `$k` switches map handling for kernel addresses.
  - `$q`/`$Q` exits.
  - `$w` changes line width and `$s` changes symbol offset tolerance.
  - `$m` prints symbol/core maps.
  - `$r`/`$R` print registers.
  - `$f`/`$F` print floating-point registers.
  - `$c`/`$C` stack-trace using machine-specific `ctrace`.
  - `$e` prints external globals and their current values.
  - `$b`/`$B` prints breakpoints.
  - `$M` selects a machine by name.
- `ptrace()` is the stack-trace callback; it prints function name, parameters, source location, caller, and optionally locals.
- `getfname()` parses a file name up to end-of-record.
- `redirin()` opens input files directly or under `Ipath`.
- `printmap()`, `printsym()`, `printsource()`, `printpc()`, `printlocals()`, and `printparams()` provide display helpers.

Notable implementation details:
- `$C` traces locals as well as call frames.
- `printfp()` delegates register formatting to machine-specific `fpformat()`.
- `printpc()` reads `mach->pc`, resolves source and symbol offsets, and disassembles through `machdata->das()`.
