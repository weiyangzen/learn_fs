# sources/storage-engines/foundationdb/fdbserver/tlog/TLogServer.cpp

## Purpose
`TLogServer.cpp` implements the FoundationDB transaction log server actor. It owns the shared physical TLog state for one worker, multiplexes one active and multiple old log generations, receives commit RPCs, makes commits durable through a disk queue, spills old log data into a key-value store, serves peek/pop/lock/recovery RPCs, and restores TLog state from disk after process restart. It is a central durability and recovery component for tag-partitioned log systems.

## Important APIs, Types, And Functions
The public surface is the `tLog(...)` actor declared in `TLogServer.h` plus `effectiveTLogMinAvailableSpaceRatio()`. Internally, `TLogQueueEntryRef` is the durable queue entry for normal commits, while `AlternativeTLogQueueEntryRef` serializes already-parsed recovered messages without rebuilding a single commit blob. `TLogQueue` wraps `IDiskQueue` with packet framing, valid flags, recovery zero-fill, version-location indexing, commit, pop, and forget-before support.

`TLogData` is shared process-level state: persistent stores, active/old log maps, pop/spill order, commit queue coordination, memory/durable byte accounting, flow locks, log-system cache, disk-space controls, and histogram/counter metrics. `LogData` is per-log-generation state: version progress, known committed state, tag data, recovery state, spill metadata, pop tracking, peek trackers, log-system consumer, and role/counter registration. `LogData::TagData` tracks per-tag in-memory messages, popped versions, persistent popped state, popped disk locations, and old-generation recovery participation.

Key actors/functions include `tLogStart`, `tLogCore`, `ServeTLogInterface::run`, `tLogCommit`, `commitQueue`, `doQueueCommit`, `updateStorageLoop`, `updatePersistentData`, `popDiskQueue`, `tLogPeekMessages`, `tLogPeekStream`, `tLogPopCore`, `tLogLock`, `pullAsyncData`, `restorePersistentState`, `initPersistentState`, `rejoinClusterController`, `respondToRecovered`, and `trackRecoveryReq`.

## Control Flow
Startup enters `tLog`, initializes the IKVS, either verifies an empty disk queue plus writes the format key or calls `restorePersistentState`, then starts shared actors for queue commits, storage spilling, and role tracing. It listens for `InitializeTLogRequest`s, caches duplicate recruitment requests by recruitment ID, and launches `tLogStart`.

`tLogStart` creates a `TLogInterface`, stops older active logs, builds `LogData`, persists initial metadata, optionally pulls recovery data from older log systems, sends recovery-finished/track-recovery handlers, waits until the commit queue has begun processing, replies with the interface, and then delegates to `tLogCore`. `tLogCore` starts endpoint servers, failure handling, metrics tracing, peek tracker cleanup/logging, and log-router pull loops for non-primary logs. Removal or recruitment failure flows through `removeLog`.

Commit flow waits for the requested previous version, applies memory backpressure, appends messages to per-tag structures, writes a queue entry, updates unknown committed version tracking if version-vector unicast is enabled, advances `logData->version`, and waits for `queueCommittedVersion` before replying. `commitQueue` serializes durable queue commits for the one non-stopped active log, while `doQueueCommit` commits `TLogQueue`, advances durable known-committed/version state, publishes log-router pops, and unblocks any old logs that missed their final queue commit.

Peek flow normalizes special tag IDs, enforces streaming sequence order through `peekTracker`, waits for requested versions when safe, reads from persistent spill data and/or in-memory deques, handles popped replies, batches empty peeks, supports streamed replies, and records per-peek latency/size metrics. Pop flow updates per-tag popped versions, handles pseudo localities via the current log system, stores delayed pop requests during snapshot ignore windows, and triggers old-generation recovery bookkeeping.

## State And Persistence Behavior
The durable queue stores framed TLog queue entries with an outer size field, a versioned payload, and a one-byte valid flag. On recovery, incomplete trailing packets are zero-filled and ignored, preserving packet-level atomicity on top of byte-prefix `IDiskQueue` durability.

The IKVS persistent format uses keys for format, protocol version, spill type, recovery count, current version, known committed version, recovery location, locality, log-router tag count, transaction-state tag count, per-tag spilled message data, per-tag queue reference batches, and per-tag popped versions. `updatePersistentData` spills messages by value for selected tags and by reference for most mutation tags, commits the IKVS, then erases durable in-memory data and updates byte accounting. `popDiskQueue` computes the earliest still-needed queue location from reference-spilled tags and queue committed location and calls `TLogQueue::pop`.

Restoration reads persistent metadata, reconstructs stopped `LogData` objects, restores persisted popped tags, replays queue entries from the recovery location into memory, periodically spills during large queue recovery, starts old-log serving actors, and re-registers with the cluster controller. Shutdown disposes persistent data/queue only for permanent worker removal or recruitment failure; otherwise it closes them.

## Dependencies And Integration Points
This file integrates with Flow actors, `TLogInterface`, `LogSystem` and `LogSystemConsumer`, `IDiskQueue`, `IKeyValueStore`, `ServerDBInfo`, cluster-controller rejoin RPCs, role tracing, transaction debug tracing, simulation policy hooks, failure monitoring, histograms/counters, and knobs from `SERVER_KNOBS`. It is built around FoundationDB actor semantics and priority scheduling.

## Risks And Edge Cases
Major risk areas are durability ordering between in-memory version state, disk queue commits, and IKVS spill commits; recovery correctness across partial queue commits; memory accounting and hard-limit backpressure; old generation retention and popped-version tracking; concurrent recruitment/stop/removal races; stream peek sequence obsolescence; log-router pseudo-locality mapping; and low-disk recovery failure behavior. The reference-spill path depends on accurate `versionLocation` data and queue locations. Several comments flag known complexity, including O(n) tag scans, queue forget cost, and spill behavior for inactive shared TLogs.

## Test Signals
The file includes a unit test for `VERSION_MESSAGES_OVERHEAD_FACTOR` using a counting deque allocator. Additional direct signals come from `TestTLogServer.cpp`, which drives commit, peek, pop, and recovery-generation flows through `tLog`. Many simulation-only paths use `buggify`, `CODE_PROBE`, and simulation policy gates to exercise partial commits, slow recovery, old generation GC blocking, and queue-recovery memory pressure.
