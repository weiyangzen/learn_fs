# File Research: sources/os/plan9/9front/sys/src/cmd/db/runpcs.c

Purpose: Breakpoint lifecycle and run-loop logic for `db`.

Key behavior:
- `runpcs()` drives single-step or continue loops, handles current breakpoint skip logic, installs/removes breakpoints, processes notes, executes breakpoint commands, and returns whether execution stopped at a breakpoint.
- `endpcs()` kills or detaches current process state and resets temporary breakpoints.
- `setup()` starts a debugged process and marks process-control active.
- `execbkpt()` single-steps over a breakpoint then restores it.
- `scanbkpt()` finds a breakpoint by address.
- `setbp()` installs all active breakpoints into process memory.
- `delbp()` removes installed breakpoints.

Notable details:
- Breakpoints transition through `BKPTSET`, `BKPTSKIP`, `BKPTTMP`, and `BKPTCLR`.
- Actual process `/proc` control is in `trcrun.c`; this file orchestrates debugger semantics.
