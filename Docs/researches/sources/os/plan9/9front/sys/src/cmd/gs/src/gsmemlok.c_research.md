# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsmemlok.c

Implements a monitor-locked wrapper around another Ghostscript memory allocator.

Key behavior:
- Builds a full `gs_memory_procs_t` table where each operation enters a `gx_monitor_t`, calls the target allocator, then leaves the monitor.
- `gs_memory_locked_init` sets procedure table, target, inherited library context, and allocates the monitor from the target.
- `gs_memory_locked_release` frees wrapper-owned structures, not target allocations.
- `gs_memory_locked_target` exposes the wrapped allocator.
- `gs_locked_free_all` only releases wrapper structures/allocator and cached stable wrapper; it does not free target data.
- `gs_locked_stable` lazily wraps the target’s stable allocator unless the target is already stable.
- All alloc/free/status/root/enable-free procedures delegate under the monitor.

Dependencies:
- Uses `gxsync.h` monitor APIs through `gsmemlok.h`.
- Delegates to the target allocator’s procedure table.

Research notes:
- This wrapper does not track allocations itself.
- It is used by `gsmalloc.c` as the first wrapper around the heap allocator before retrying behavior.
