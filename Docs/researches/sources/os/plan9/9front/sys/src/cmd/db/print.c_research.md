# File Research: sources/os/plan9/9front/sys/src/cmd/db/print.c

Purpose: `$` meta-command implementation and higher-level printing for `db`.

Key behavior:
- `printtrace()` handles:
  - input/output redirection,
  - attach by pid,
  - kernel mapping adjustment,
  - quit,
  - line width and symbol offset settings,
  - map display,
  - register and floating-register printing,
  - C stack traces and locals,
  - extern/global symbol values,
  - breakpoint listing,
  - machine selection.
- `ptrace()` is the stack trace callback used by `machdata->ctrace()`.
- `printmap()` prints map segments and backing files.
- `printsym()` dumps raw symbol table entries.
- `printsource()` prints file:line for an address.
- `printpc()` prints current pc source, symbol offset, and disassembled instruction.
- `printlocals()` and `printparams()` print local variables and parameters from symbol metadata.
- `redirin()` opens command input files, falling back under `Ipath`.

Notable details:
- `$C` stack tracing prints locals after each frame.
- `printparams()` assumes parameters are at offsets from frame pointer after saved pc.
