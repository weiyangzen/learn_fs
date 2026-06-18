# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/libunbound/libworker.h

Internal header for the libunbound library worker.

Defines:
- `struct libworker`: per-worker state with thread number, owning `ub_ctx`, background/thread flags, quit flag, worker-local `module_env`, comm base, outside-network backend, random state pointer, and SSL context pointer.

Declares:
- `libworker_bg()` for background worker creation.
- `libworker_fg()` for blocking foreground resolution.
- `libworker_create_event()` / `libworker_delete_event()` for external event-loop workers.
- `libworker_attach_mesh()` for event-driven async query attachment.
- `libworker_alloc_cleanup()` for cache cleanup on allocator reuse.
- `libworker_enter_result()` for converting parsed DNS packets into public `ub_result`.

Role:
- Captures the private boundary between libunbound context/query code, the resolver mesh, and the outside network backend.
- Distinguishes libunbound worker APIs from daemon worker APIs declared in `worker.h`.
