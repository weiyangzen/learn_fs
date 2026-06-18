# File Research: sources/virtualization/qemu/block/blkreplay.c

This file implements the `blkreplay` filter for deterministic record/replay synchronization of block I/O completions.

Key behavior:
- `blkreplay_open()` opens an `image` child and propagates `BDRV_REQ_WRITE_UNCHANGED` support for write and zero flags.
- Each I/O wrapper obtains a replay request id with `blkreplay_next_id()`, performs the child I/O synchronously in coroutine context, creates a replay block event, yields, and resumes only when the replay-scheduled bottom half fires.
- Supported operations include read, write, write-zeroes, discard, flush, and snapshot goto.
- `block_request_create()` creates a bottom half in the coroutine's AioContext and registers it with `replay_block_event()`.
- `blkreplay_bh_cb()` wakes the coroutine, deletes the bottom half, and frees request state.

Snapshot behavior:
- `blkreplay_snapshot_goto()` obtains the file child under graph read lock, then delegates to `bdrv_snapshot_goto()`.

Filesystem/block relevance:
- This filter is not a storage format; it is determinism infrastructure.
- It makes block I/O completion ordering reproducible across record/replay, which matters for debugging guest filesystems and storage race conditions.

Potential pitfalls:
- The child I/O is performed before the coroutine yields for deterministic completion scheduling.
- The filter has no private instance state.
- Replay correctness relies on integration with the global replay subsystem.
