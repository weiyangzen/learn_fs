# File Research: sources/os/plan9/9front/sys/src/cmd/db/fns.h

Purpose: Function prototype header for the `db` debugger.

Coverage:
- Command parsing and command helpers.
- Expression parsing and token reading.
- Output and input redirection.
- Map setup and manipulation.
- Register access and printing.
- Breakpoint/process control.
- Stack trace, symbol, source, local/parameter printing.
- Process attach/run/kill/note handling.

Notable details:
- Includes vararg checking for `dprint`.
- Exposes `rget()`/`rput()` used by libmach callbacks and expression evaluation.
