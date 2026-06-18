# File Research: sources/virtualization/nbdkit/plugins/memory/memory.c

This plugin implements a writable volatile memory-backed block device using pluggable allocator backends.

Configuration:
- Requires `size=<SIZE>`.
- Optional `allocator=<type>` defaults to `sparse`.
- Exposes debug variable `memory_debug_dir` for allocator directory operations.

Lifecycle:
- `.get_ready` creates the selected allocator and passes the size hint.
- `.unload` frees the allocator.
- No per-connection handle is needed.

Capabilities:
- Parallel thread model.
- Native FUA because flush is a no-op.
- Multi-connection safe.
- Native cache.
- Fast zero supported.
- Exposes allocator-provided extents.

I/O:
- `.pread`, `.pwrite`, `.zero`, `.trim`, and `.extents` delegate to allocator function pointers.
- `.trim` is implemented as zero.
- `.flush` returns success.

Integration:
- Uses `common/allocators` abstraction, so sparse/compressed/other behavior is selected outside this file.
- `dump_plugin` advertises `mlock` and `zstd` availability.

Risks:
- Correctness and concurrency depend on allocator implementation.
- Assertions enforce expected flags but are compiled out under `NDEBUG`.
