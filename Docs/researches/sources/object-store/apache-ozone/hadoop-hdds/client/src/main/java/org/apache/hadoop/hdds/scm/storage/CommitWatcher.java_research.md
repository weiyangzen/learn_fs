# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/CommitWatcher.java

## Purpose
`CommitWatcher` specializes `AbstractCommitWatcher` for `ChunkBuffer`-backed Ratis block writes. It watches commit indexes and releases committed write buffers back to `BufferPool`.

## Important APIs and Types
The constructor accepts a `BufferPool` and `XceiverClientSpi`. `releaseBuffers(long)` removes buffers associated with a committed log index, releases them to the pool, and accounts acknowledged data length. `cleanup()` delegates to the abstract watcher cleanup.

## Control Flow
`RatisBlockOutputStream` records commit index to buffer-list mappings after successful putBlock. When watch-for-commit completes, the abstract watcher calls `releaseBuffers`, which sums each buffer's position as acknowledged bytes and returns the buffer to the pool.

## State and Persistence Behavior
This class owns only a reference to `BufferPool`; commit maps and counters live in the abstract superclass. It affects in-memory buffer lifecycle, not persisted block data.

## Dependencies and Integration Points
Used only by `RatisBlockOutputStream`. It depends on Ratis client commit watching through `AbstractCommitWatcher` and on `BufferPool.releaseBuffer`.

## Risks
The code comment notes possible ordering issues when concurrent watch-for-commit executions update flushed length semantics. If buffers are released under the wrong index, writers may reuse data before replication is sufficiently acknowledged.

## Test Signals
Covered indirectly by `RatisBlockOutputStream` and `BlockOutputStream` tests that assert buffer release, acknowledged data length, flush, and close behavior.
