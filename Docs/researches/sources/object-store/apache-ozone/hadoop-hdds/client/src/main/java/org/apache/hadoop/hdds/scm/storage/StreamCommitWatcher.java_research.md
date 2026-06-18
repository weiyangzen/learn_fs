# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/StreamCommitWatcher.java

## Purpose
`StreamCommitWatcher` specializes `AbstractCommitWatcher` for `StreamBuffer` lists. It releases stream buffers from an external list once the associated Ratis commit index is replicated.

## Important APIs and Types
The constructor accepts an `XceiverClientSpi` and a shared `List<StreamBuffer>`. `releaseBuffers(long)` removes buffers tracked for a commit index, subtracts them from the shared list, and increments acknowledged data length by each buffer's position.

## Control Flow
When the abstract watcher completes a commit watch, this class removes the committed buffers from both the superclass index map and the caller-provided buffer list. It then updates total ack length.

## State and Persistence Behavior
The only local state is a reference to the shared buffer list. It does not persist data; it controls in-memory buffer retention.

## Dependencies and Integration Points
Used by streaming write paths that use `StreamBuffer` rather than `ChunkBuffer`. It depends on `AbstractCommitWatcher` and Ratis `XceiverClientSpi`.

## Risks
The shared list must be safe for the access pattern used by callers. Removal is by object equality, so duplicate/equal wrappers could cause surprising behavior if equality is later added to `StreamBuffer`.

## Test Signals
No direct test was identified. Behavior should be covered by any stream write tests that assert ack length and buffer list shrinking.
