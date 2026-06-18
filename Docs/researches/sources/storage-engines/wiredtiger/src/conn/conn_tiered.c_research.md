# sources/storage-engines/wiredtiger/src/conn/conn_tiered.c

## Purpose
This file implements connection-level tiered storage worker infrastructure. It processes queued work to copy flushed local objects to shared storage, run storage-source post-flush completion, and remove local objects after retention.

## Important APIs, Types, and Functions
Public entry points are `__wti_conn_tiered_init`, `__wti_conn_tiered_destroy`, `__wti_tiered_storage_create`, and `__wti_tiered_storage_destroy`. Core helpers include `__tier_storage_remove_local`, `__tier_flush_meta`, `__tier_release_local_object`, `__tier_do_operation`, `__tier_operation`, `__tier_storage_finish`, `__tier_storage_copy`, `__tier_storage_remove`, and `__tiered_server`. Key types are `WT_CONN_TIERED`, `WT_TIERED_WORK_UNIT`, `WT_TIERED`, `WT_STORAGE_SOURCE`, `WT_FILE_SYSTEM`, `WT_BM`, and metadata tracking structures.

## Control Flow and Behavior
Connection-tiered init creates the work queue and locks. Create skips the tiered server when disaggregated storage is configured, allocates flush/storage conditions, sets `WT_CONN_SERVER_TIERED`, opens a dedicated internal session, sets the first-flush flag, and starts the server.

The server waits for interval or signal, then runs copy, finish, and remove phases. Copy waits for a checkpoint after flush completion, uses checkpoint generation to avoid processing work units from tables added during an active checkpoint, and calls `__tier_operation` for eligible flush work. A flush operation builds local/object names, prefixes object names with bucket prefix, calls `storage_source->ss_flush`, then under checkpoint and schema locks updates metadata by removing the local file entry and adding flush time/timestamp to the object entry. It releases the local object through the block manager, queues a flush-finish work unit, and queues future local removal. Finish calls `ss_flush_finish`. Remove-local checks retention time, removes local object files if no handle keeps them open, or requeues with a new deadline.

## State and Persistence
Volatile state includes work queues, locks, conditions, server thread/session, interval, first-flush and flush-checkpoint-complete flags. Persistent state changes happen in metadata: local file metadata is removed after successful flush, object metadata records flush time and timestamp, and local files may be removed after retention. Unfinished work is intentionally recoverable on startup rather than forced at shutdown.

## Dependencies and Integration Points
The file depends on tiered naming helpers, metadata tracking, checkpoint/schema locks, block-manager object switching, storage-source flush APIs, bucket filesystem, condition variables, timing stress flags, and connection worker startup. It is mutually excluded with disaggregated storage in `conn_open.c`.

## Risks
Risks include metadata becoming inconsistent if flush succeeds but metadata update fails, dropped handles while work units still reference tiered structures, network/storage-source timeouts, local removal while a file handle is still open, generation races with checkpoint, and shutdown with queued work that must be recovered later.

## Test Signals
Signals include successful flush_tier metadata transitions, storage-source `ss_flush`/`ss_flush_finish` calls, local object retention/removal behavior, restart recovery of unfinished work, disaggregated mode not starting tiered server, and timing-stress tests around flush-finish.
