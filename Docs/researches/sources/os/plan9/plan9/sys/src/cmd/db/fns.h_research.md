# File Research: sources/os/plan9/plan9/sys/src/cmd/db/fns.h

Function prototype header for Plan 9 `db`.

Key contents:
- Declares debugger command, expression, formatting, input, output, process-control, symbol, register, map, breakpoint, and setup functions.
- Includes vararg checking for `dprint`.
- Exposes interfaces split across files not all in this group, including `pcs.c`, `runpcs.c`, `setup.c`, `regs.c`, and output/print modules.

Research notes:
- Useful as the module dependency map for `db`: command parsing, expression parsing, and formatting files in this group call many functions declared here but implemented elsewhere.
