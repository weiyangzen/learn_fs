# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/waserror.c

This file implements the core hosted Plan 9 error unwinding helpers.

Key behavior:
- `pwaserror` returns a new error label slot and increments `up->nerrlab`.
- `nexterror` long-jumps to the most recent saved label.
- `error` stores an error string in `up->errstr` and unwinds.

Important details:
- Callers use Plan 9's `waserror` macro around these helpers.
- `ERRMAX` bounds copied error text.
