# File Research: sources/os/plan9/9front/sys/src/9/omap/syscall.c

OMAP syscall and user-notification register handling.

Key behavior:
- `syscall` is entered from SWI exception assembly, adjusts PC, validates user mode, dispatches through `systab`, stores return values, handles errors/notes/procctl, and exits through `kexit`.
- `notify` builds a user notification frame and redirects execution to the user notify handler.
- `noted` validates and restores notification frames according to Plan 9 note action.
- `execregs` initializes registers for a new exec image.
- `forkchild` copies the parent `Ureg`, sets child return value to 0, and arranges `forkret`.

Research notes:
- This file is architecture-specific glue around generic Plan 9 syscall and note semantics.
