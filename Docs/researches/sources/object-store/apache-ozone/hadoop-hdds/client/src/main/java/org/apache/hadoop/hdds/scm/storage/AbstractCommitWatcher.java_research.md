# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/AbstractCommitWatcher.java

Purpose: Shared commit-watch helper for write streams. It watches Ratis commit indexes and releases associated buffers once data has replicated sufficiently.

Important APIs/types/functions: `updateCommitInfoMap` associates commit indexes with buffers. `watchOnFirstIndex` and `watchOnLastIndex` watch the lowest or highest pending index. `watchForCommitAsync` deduplicates in-flight watch requests per index. `adjustBuffers` releases buffers for indexes up to the committed index. Subclasses implement `releaseBuffers(long)`. `totalAckDataLength` tracks acknowledged data length.

Control flow: When a watch is requested, a memoized future is inserted in `replies` only if absent. The client's `watchForCommit` future completes the shared future, removes it from the reply cache, and adjusts buffers based on returned log index. Synchronous `watchForCommit` wraps interruptions/execution failures as IOExceptions and releases buffers up to the client's replicated minimum.

State and persistence behavior: Holds a concurrent sorted commit-index-to-buffer map, a concurrent reply-future cache, the xceiver client, and ack length counter. State is in-memory and cleared by `cleanup`.

Dependencies and integration points: Used by stream output implementations such as `BlockDataStreamOutput` through concrete watchers. Depends on `XceiverClientSpi.watchForCommit`.

Risks: `adjustBuffers` streams over `commitIndexMap.keySet()` while `releaseBuffers` likely removes entries; concurrent map semantics make this possible, but subclass side effects need care. Failed watches may release only up to replicated minimum, leaving buffers for retry paths. Duplicate watch future handling relies on strict removal identity.

Test signals: Tests should cover duplicate watch coalescing, first/last index behavior, buffer release ordering, exception release behavior, and cleanup.
