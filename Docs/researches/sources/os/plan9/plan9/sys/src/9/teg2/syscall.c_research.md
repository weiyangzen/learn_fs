# File Research: sources/os/plan9/plan9/sys/src/9/teg2/syscall.c

ARM machine-dependent syscall and Plan 9 note handling.

Key behavior:
- `syscall(Ureg*)` validates user mode, reads syscall number from `r0`, copies syscall args from the user stack, dispatches through `systab`, writes return value to `r0`, handles tracing, notes, delayed scheduling, and `kexit`.
- `notify` builds an `NFrame` on the user stack and redirects execution to `up->notify`.
- `noted` validates and restores user register state after note handling, preserving privileged PSR bits.
- `execregs` sets entry PC and stack for `exec`.
- `forkchild` creates a saved return frame for a forked child so it returns `0` in user mode.

Notes:
- Uses explicit cache writeback calls around syscall/note paths because the system was more stable with them.
- Hooks into FPU lifecycle for notes, `rfork`, and `exec`.
