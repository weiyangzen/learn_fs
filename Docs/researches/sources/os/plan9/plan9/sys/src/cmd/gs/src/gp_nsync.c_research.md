# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_nsync.c

Read status: complete.

Purpose: dummy thread/semaphore/monitor implementation for builds without real threading.

Main logic:
- Semaphores are represented as an integer count.
- `gp_semaphore_wait` fails with `gs_error_unknownerror` if the count is zero; it does not block.
- `gp_semaphore_signal` increments the count.
- Monitors store a dummy owner marker and fail if entered twice or left without ownership.
- `gp_create_thread` always returns `gs_error_unknownerror`.

Filesystem/storage relevance:
- None directly. It affects concurrency availability for any shared cache or device code compiled with this backend.

Notable behavior:
- This is intentionally not a real synchronization implementation.
