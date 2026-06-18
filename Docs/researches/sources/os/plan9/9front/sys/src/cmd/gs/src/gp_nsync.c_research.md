# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_nsync.c

Dummy synchronization and threading implementation.

Key behavior:
- Represents semaphores as a simple integer counter.
- `wait` fails with `unknownerror` when the counter is zero instead of blocking.
- Represents monitors with a dummy owner pointer and detects simple enter/leave misuse.
- `gp_create_thread` always returns `unknownerror`.

Research notes:
- This is for single-threaded or no-thread builds where real synchronization is unavailable.
