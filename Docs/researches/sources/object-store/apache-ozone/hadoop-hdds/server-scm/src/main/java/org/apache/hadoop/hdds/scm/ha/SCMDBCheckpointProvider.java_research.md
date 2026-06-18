<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMDBCheckpointProvider.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMDBCheckpointProvider.java

## Purpose

`SCMDBCheckpointProvider` creates and streams SCM RocksDB checkpoints to an output stream, cleaning up checkpoint resources afterward.

## Important APIs, Types, and Functions

The main API is `writeDBCheckPointToSream(OutputStream, boolean)`. It uses `DBStore.getCheckpoint`, `HddsServerUtil.writeDBCheckpointToStream`, `DBCheckpoint.cleanupCheckpoint`, and logs duration.

## Control Flow

The method validates that the store exists, obtains a checkpoint with optional flush, rejects null checkpoints or missing locations, streams the checkpoint directory/archive to the caller, logs elapsed time, rethrows IO errors, and always attempts checkpoint cleanup.

## State and Persistence Behavior

State is a transient `DBStore` reference. The DB checkpoint is a temporary persistent snapshot created by the DB layer and cleaned up in `finally`.

## Dependencies and Integration Points

It integrates with inter-SCM gRPC streaming, DBStore checkpoint support, and HDDS checkpoint streaming utilities.

## Risks and Edge Cases

The method name contains `Sream`, which is API spelling. If the store is null it logs and returns without signaling failure. Cleanup failures are logged but not rethrown. An empty file name returns without streaming.

## Test Signals

Tests should cover successful stream and cleanup, null store behavior, null checkpoint rejection, null checkpoint location rejection, streaming IO error propagation, flush flag propagation, and cleanup failure logging.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMDBCheckpointProvider.java -->
