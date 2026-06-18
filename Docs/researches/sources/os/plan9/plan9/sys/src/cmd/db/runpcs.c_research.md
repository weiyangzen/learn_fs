# File Research: sources/os/plan9/plan9/sys/src/cmd/db/runpcs.c

This file coordinates high-level execution of the debugged process and breakpoint state.

Key behaviors:
- Defines global breakpoint list `bkpthead`, breakpoint-installed flag `bpin`, process `pid`, note buffer `note`, and process-ending state.
- `runpcs()` drives repeated single-step or continue execution according to `loopcnt`.
- Handles breakpoint skip logic, temporary breakpoint clearing, breakpoint command execution, and count reset.
- `endpcs()` kills/cleans an active process, clears temporary breakpoints, and resets installed breakpoints to `BKPTSET`.
- `setup()` starts a fresh process with `startpcs()`.
- `execbkpt()` steps over a breakpoint and re-enables it.
- `scanbkpt()` finds a breakpoint at an address.
- `setbp()` installs all active breakpoints; `delbp()` removes them.

Notable implementation details:
- When stopped for real notes, `runpcs()` keeps note delivery pending.
- `BKPTSKIP` is used to avoid immediately re-triggering a breakpoint while stepping past it.
- `runpcs()` writes `dot` to the PC when `adrflg` is set before running.
