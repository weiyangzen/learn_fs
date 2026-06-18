# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/console.c

Console-side wrappers around cwfs 9P handlers and low-level destructive/admin helpers.

Important behavior:
- `con_session`, `con_attach`, `con_clone`, `con_walk`, `con_open`, `con_create`, `con_read`, `con_write`, and `con_remove` synthesize `Fcall` structures and call the same 9P operations under `mainlock`.
- `con_create()` injects console uid/gid into global console state before creating.
- `doclri()` clears a dentry directly without normal emptiness checks.
- `con_fstat()` prints raw dentry metadata and block pointers.
- `con_clri()` invokes the direct-clear path.
