<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/live_restore/live_restore_private.h -->
# sources/storage-engines/wiredtiger/src/live_restore/live_restore_private.h

## Purpose
Defines private live-restore constants, lock macros, state enums, layered file-system structures, file-handle state, and background-server queue structures used only by the live-restore implementation.

## Important APIs, Types, and Functions
Constants include `.stop` and `.lr_tmp` suffixes, offset/bit conversion macros, `WTI_BITMAP_END`, `WTI_DEST_COMPLETE`, and the cleanup timing-stress delay. `WTI_LIVE_RESTORE_FILE_HANDLE` wraps a `WT_FILE_HANDLE`, destination/source handles, back pointer, allocation size, file type, per-file `WT_RWLOCK`, bitmap bit count, and bitmap memory. Lock macros encapsulate file-handle write locking, server queue locking, and state locking. `WTI_LIVE_RESTORE_FS_LAYER_TYPE`, `WTI_LIVE_RESTORE_FS_LAYER`, `WTI_LIVE_RESTORE_STATE`, `WTI_LIVE_RESTORE_FS`, `WTI_LIVE_RESTORE_WORK_ITEM`, and `WTI_LIVE_RESTORE_SERVER` model layers, state machine, file-system config, migration queue entries, and worker-thread server state.

## Control Flow
This header has no runtime code, but the macros determine the lock discipline used throughout live restore. The state enum defines the legal sequence `NONE -> BACKGROUND_MIGRATION -> CLEAN_UP -> COMPLETE`. The server queue is a `TAILQ` of URIs consumed by worker threads. `WTI_DEST_COMPLETE` treats a closed or absent source handle as the signal that a file no longer needs migration work.

## State and Persistence Behavior
The in-memory state mirrors persisted turtle metadata and per-file checkpoint metadata. The file-system stores source/destination homes, thread/read-size configuration, current live-restore state, and state lock. The file handle stores migration progress until serialized by checkpoint; once migration completes, the source handle is closed and the bitmap freed. Server counters back progress stats and cleanup decisions.

## Dependencies and Integration Points
Requires typedefs from `wt_internal.h` and is included by `live_restore_fs.c`, `live_restore_server.c`, and `live_restore_state.c`. Prototypes expose private cross-file calls such as state get/set/init/validation, migration-complete checks, stop-file cleanup, and restoring a single file.

## Risks and Edge Cases
The lock macros rely on callers passing valid session/file-system/server pointers; incorrect lock ordering could deadlock with turtle or metadata locks. Offset macros reference `lr_fh->allocsize` and assume correct local variable naming. The comments explicitly allow rare lock exceptions only where implementation code documents them. State transitions must remain ordered because cleanup and non-live-restore validation rely on that monotonic progression.

## Test Signals
Compile-time signals catch structure/prototype drift across the three implementation files. Runtime signals come from live-restore API and unit tests, especially tests that manipulate bitmap state, queue cleanup, state transitions, stop-file behavior, and cleanup timing-stress paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/live_restore/live_restore_private.h -->
