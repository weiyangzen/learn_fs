# sources/storage-engines/wiredtiger/src/meta/meta_track.c

## Purpose
Provides a non-transactional metadata operation log used to roll back failed schema operations and apply post-commit filesystem cleanup.

## Important APIs, Types, and Functions
The private `WT_META_TRACK` records operations such as checkpoint resolution, deferred file drop, deferred object drop, file operation rollback, handle lock release, metadata remove, and metadata set. Public helpers include `__wt_meta_track_on`, `__wt_meta_track_off`, `__wt_meta_track_sub_on`, `__wt_meta_track_sub_off`, `__wt_meta_track_checkpoint`, `__wti_meta_track_insert`, `__wti_meta_track_update`, `__wt_meta_track_fileop`, `__wt_meta_track_drop`, `__wt_meta_track_drop_object`, `__wt_meta_track_handle_lock`, `__wt_meta_track_init`, `__wt_meta_track_destroy`, and `__wt_meta_track_discard`.

## Control Flow
Tracking turns on by incrementing a nest counter and allocating the operation array. Each metadata or filesystem action appends a record, duplicating strings or saving handles as needed. `__wt_meta_track_off` disables tracking at the outer level, optionally checkpoints/log-syncs metadata, then either applies records in forward order or unrolls in reverse order. Subtracking lets a suffix of operations be applied independently before the enclosing operation finishes.

## State and Persistence Behavior
Tracking state lives on `WT_SESSION_IMPL` as a dynamically grown operation array, next pointer, subtransaction pointer, allocation size, and nesting count. Commit paths may checkpoint or log-sync metadata, resolve block-manager checkpoints, release handles, and physically drop files/objects. Unroll paths restore metadata values, remove newly inserted metadata, undo creates/renames when possible, release locked handles, and mark newly created handles for discard.

## Dependencies and Integration Points
It integrates metadata updates, schema operations, block manager checkpoint resolution, filesystem rename/remove, object storage drops, session handle locking, sweep thread wakeup, log checkpoint sync, and the separate `meta_ckpt_session` used when logging is disabled.

## Risks and Edge Cases
The operation log is not a general transaction system: file removes cannot be undone, so schema code must order operations carefully. Nested tracking must leave the outer operation array consistent after sub-off. If apply/unroll fails, the connection panics because metadata state may be inconsistent. Metadata checkpoints are skipped in in-memory or no-op cases. The non-logged path copies transaction time-point state into `meta_ckpt_session`, so isolation and locking assumptions matter.

## Test Signals
Failed create/drop/rename/alter tests should verify metadata and filesystem rollback. Checkpoint failure injection should exercise `WT_ST_CHECKPOINT` unroll. Logged and non-logged metadata updates, in-memory drops, tiered object drops, and session close cleanup validate the major paths.
