# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsmemret.c

Implements a retrying allocator wrapper around another allocator.

Key behavior:
- Builds `retrying_procs`, a full `gs_memory_procs_t` table.
- Allocation-like operations call the target allocator; if the result is null, they invoke a recovery closure and retry while it returns `RECOVER_STATUS_RETRY_OK`.
- Default recovery closure is `no_recover_proc`, which never retries.
- Free, status, object-size/type, unregister-root, enable-free, and consolidate-free directly forward to the target without retry loops.
- `gs_memory_retrying_init` sets procs, target, inherited library context, `non_gc_memory`, and default recovery closure.
- `gs_memory_retrying_set_recover` installs custom recovery callback/data.
- `gs_memory_retrying_release` releases wrapper structures only.
- `gs_retrying_stable` lazily wraps target stable allocator unless target stable allocator is the same target.

Dependencies:
- Implements interface declared in `gsmemret.h`.
- Assumes target allocator supplies complete `gs_memory_t` procs.

Research notes:
- This wrapper is designed to give clients a hook to free memory or trigger collection after failed allocation.
- It does not own allocations and does not free target data.
