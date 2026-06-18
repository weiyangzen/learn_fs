# File Research: sources/os/linux/linux/fs/xfs/xfs_trans_ail.c

## Purpose

Implements XFS Active Item List (AIL) management. The AIL tracks committed but not-yet-written log items in LSN order so the log tail can advance only after metadata reaches stable storage.

## Main Responsibilities

- Maintains the sorted AIL list and minimum/tail LSN queries.
- Provides cursor-safe AIL traversal for pushers and other scanners.
- Inserts, moves, and deletes log items while updating log tail space.
- Runs the `xfsaild` kernel thread to push dirty metadata items toward disk.
- Handles failed buffer resubmission through delayed-write queues.
- Implements push-all synchronization for unmount/quiesce paths.
- Initializes and destroys the per-mount AIL state.

## Important Invariants

- AIL ordering is by ascending `li_lsn`.
- Cursors must be invalidated when pointed-at items are removed or moved.
- Push callbacks can drop and reacquire the AIL lock, so callers must not dereference items after push.
- Log tail updates happen only when the minimum AIL LSN changes or when explicitly forced.
- Failed buffer items must be queued for I/O before clearing failed state to avoid transient zero-reference use-after-free hazards.
- The push daemon backs off when too many items are pinned, locked, or already flushing.

## Dependencies

Uses XFS log, CIL, buffer delayed-write, log item ops, stats, tracepoints, shutdown state, and kernel kthread/freezer infrastructure.

## Research Notes

This is correctness-critical for log-space reclamation. The most important behavior is preserving AIL order while allowing concurrent item removal and push callbacks that temporarily drop locks.
