# sources/storage-engines/pebble/wal/standalone_manager.go

## Purpose
Implements the `Manager` interface for Pebble's non-failover WAL mode, where each logical WAL maps to exactly one physical file in the primary WAL directory.

## Important APIs, Types, And Functions
`StandaloneManager` owns `Options`, a `LogRecycler`, an open directory handle, initial obsolete logs, an active `standaloneWriter`, and a mutex-protected WAL queue. Methods implement `init`, `List`, `Obsolete`, `Create`, `Stats`, `Close`, `Opts`, and `RecyclerForTesting`. `standaloneWriter` implements `Writer` through `WriteRecord`, `Close`, and `Metrics`. `firstError` preserves primary failure ordering.

## Control Flow
`init` rejects secondary-directory configuration, opens the primary WAL directory, initializes recycling, and marks all initial logs obsolete/deletable while ratcheting the minimum recyclable number. `Create` chooses either a recycled log via `ReuseForWrite` or a new file via `Create`, emits log-created events through a deferred `CreateInfo`, stats recycled size if needed, pops the recycler entry, syncs the directory, wraps the file in `vfs.NewSyncingFile`, and constructs a `record.LogWriter`. `Obsolete` removes initial and queued WALs below `minUnflushedNum`, adding some to the recycler unless `noRecycle` is set.

## State And Persistence Behavior
The queue stores live and already-flushed WAL file metadata; flushed WALs are a prefix. Active WAL size is recorded as original recycled size until close, then updated to logical writer size if larger. Directory sync after creation makes the link durable. Writer close writes the record-layer EOF trailer and syncs unless configured otherwise.

## Dependencies And Integration Points
Integrates with Pebble commit pipeline synchronization, WAL recycling, event listener callbacks, file-operation histograms, `record.LogWriter`, `vfs.SyncingFile`, and DB log-obsolescence decisions.

## Risks And Edge Cases
The implementation relies on external serialization for create/write/close. Recycled file size may be inaccurate until stat because `ReuseForWrite` may replace instead of reuse. The previous writer must be closed before a new WAL is created; otherwise two unclean tails after a crash can make recovery treat the earlier WAL as corrupt. Initial obsolete logs can contain multi-segment failover WALs and must be handled separately from the single-file queue.

## Test Signals
Coverage is indirect through WAL manager, DB open/recovery, recycling, event listener, and standalone WAL behavior tests. Metrics and `Obsolete` outputs expose live versus obsolete accounting.
