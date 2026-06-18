# File Research: sources/virtualization/nbdkit/plugins/vddk/worker.c

Implements the per-connection VDDK worker thread and command queue execution. This isolates VDDK API calls from nbdkit parallel callback threads.

Key behavior:
- `command_type_string` maps command enums to debug names.
- `send_command_and_wait` assigns a command id, appends the command to the handle queue, initializes completion mutex/condition, wakes the worker if needed, waits until the command status changes from `SUBMITTED`, destroys synchronization primitives, and returns success/failure.
- Async VDDK read/write completion callback `complete_command` updates async stats, records success/failure, logs VDDK errors, and signals the waiting caller.
- `do_stop` waits for outstanding async commands with `VixDiskLib_Wait`.
- `do_info` calls `VixDiskLib_GetInfo` and optionally logs detailed disk geometry, parent, UUID, and sector sizes.
- `do_read` and `do_write` enforce 512-byte sector alignment for offset/count, convert byte units to sectors, start timing, call `VixDiskLib_ReadAsync` or `WriteAsync`, and require `VIX_ASYNC`.
- `do_flush` waits for outstanding async work, logs but tolerates wait errors, then calls `VixDiskLib_Flush`.
- `test_can_extents` probes `VixDiskLib_QueryAllocatedBlocks` with error suppression; failures disable extents and are logged at debug level.
- Extent helpers convert VDDK allocated-block lists into nbdkit extents, inserting holes between allocated ranges. Holes are marked zero unless `single_link` is enabled.
- `get_extents_slow` queries VDDK in chunk-aligned ranges, respects VDDK maximum chunk count, handles unqueryable tail ranges as allocated data, and honors `REQ_ONE`.
- `pre_cache_extents` scans the entire readonly disk in large chunks and stores complete extents in `h->extents`.
- `get_extents_from_cache` copies cached extents into the response.
- `do_extents` pre-caches readonly extents on first use to avoid repeated slow `QueryAllocatedBlocks`; writable disks use slow per-request queries.
- `vddk_worker_thread` first probes extent support, then loops waiting on the command queue, dispatching commands, and signaling completion. Async read/write commands are retired by their VDDK callback, not immediately by the loop.

Dependencies:
- VDDK async APIs and QueryAllocatedBlocks.
- nbdkit extents API.
- pthread synchronization.
- rounding/alignment helpers.

Notes and risks:
- `send_command_and_wait` depends on caller-provided command objects remaining alive until completion; current callers use stack commands and wait synchronously.
- Read/write require sector alignment; misaligned requests return `EINVAL`.
- QueryAllocatedBlocks is documented in comments as slow and serializing, motivating readonly pre-cache.
