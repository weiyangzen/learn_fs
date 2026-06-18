# File Research: sources/virtualization/qemu/block/block-copy.c

This file implements the reusable `block-copy` engine used by backup/copy-before-write workflows to copy dirty clusters from a source child to a target child with concurrency, rate limiting, bitmap tracking, copy-range optimization, zero detection, and cancellation.

Core state:
- `BlockCopyState` stores source/target children, cluster size, max transfer, total length, write flags, mutex, in-flight bytes, current copy method, discard-source flag, active request list, active async calls, skip-unallocated flag, dirty bitmap, progress meter, shared memory limit, and rate limiter.
- `BlockCopyCallState` represents one sync or async copy call over an offset/range, with worker limits, callback, coroutine, cancellation/finished flags, sleep state, and final error information.
- `BlockCopyTask` represents a dirty chunk being copied, including the chosen method and conflict-tracked `BlockReq`.

Initialization:
- `block_copy_state_new()` validates minimum cluster size, determines effective cluster size from the target image, creates and disables an internal dirty bitmap, merges an input bitmap or marks the whole image dirty, detects image-fleecing topology, initializes shared memory/rate-limit/locks/lists, and chooses initial copy options.
- `block_copy_calculate_cluster_size()` uses target `BlockDriverInfo` and backing-chain presence to avoid unsafe cluster-size assumptions.
- `block_copy_set_copy_opts()` chooses between buffered read/write, cluster-sized buffered copy, or copy-range modes depending on compression, max transfer, and `use_copy_range`.

Task creation and tracking:
- `block_copy_task_create()` finds the next dirty area, aligns it to cluster size, clears the dirty bits, adds bytes to in-flight accounting, and registers a request-list entry.
- `block_copy_task_shrink()` returns the tail of an oversized task to the dirty bitmap and shrinks the request.
- `block_copy_task_end()` subtracts in-flight bytes, restores dirty bits on failure, updates progress remaining, and removes the request entry.
- Request-list conflict handling lets parallel copy callers cooperate and wait for intersecting tasks.

Copy methods:
- `COPY_WRITE_ZEROES` writes zeroes directly to the target.
- `COPY_RANGE_SMALL`/`COPY_RANGE_FULL` try `bdrv_co_copy_range()` and promote chunk size after success.
- Copy-range failure falls back to buffered read/write and changes later tasks to buffered copying.
- Buffered mode allocates a block-aligned bounce buffer, reads source, writes target, and records whether errors were read-side or write-side.
- Successful tasks optionally discard the copied source range when `discard_source` is enabled.

Dirty-cluster loop:
- `block_copy_dirty_clusters()` finds dirty tasks, consults block status, skips unallocated regions when requested, converts zero ranges to write-zeroes, applies rate limiting, reserves shared memory, and runs tasks directly or through an `AioTaskPool`.
- The task pool is created only when there is more work, and uses `max_workers`.
- A failed task pool returns the first negative status.

Call lifecycle:
- `block_copy_common()` inserts the call into `s->calls`, repeatedly copies dirty clusters, waits for intersecting requests if no immediate dirty bits remain, and retries when progress or wait results imply new dirty bits may exist.
- It marks the call finished atomically, invokes the callback, and removes it from the active calls list.
- `block_copy()` provides a synchronous coroutine API with timeout support.
- `block_copy_async()` starts a copy coroutine and returns a `BlockCopyCallState`.
- Call helpers expose finished/succeeded/failed/cancelled/status state and cancellation.

Control APIs:
- `block_copy_reset()` clears dirty bits and updates remaining progress.
- `block_copy_reset_unallocated()` queries source allocation and clears dirty bits for unallocated clusters.
- `block_copy_set_skip_unallocated()` toggles sync=top unallocated skipping.
- `block_copy_set_speed()` updates the rate limiter; callers must kick active call state separately.
- `block_copy_dirty_bitmap()` and `block_copy_cluster_size()` expose internal state to users such as backup jobs.

Filesystem/block relevance:
- This is the core data-copy mechanism behind incremental/full backups and copy-before-write preservation.
- It manages bitmap consistency, sparse/unallocated optimization, zero handling, and safe parallel copying across QEMU block graph children.

Potential pitfalls:
- Source and target are expected to remain in the same AioContext.
- Cancellation and finish are explicitly racy; callers may cancel an already finished call.
- `block_copy_set_speed()` does not itself wake every active call because doing so safely requires coroutine context.
- Failure restores dirty bits for the failed task so future retries can recopy the region.
