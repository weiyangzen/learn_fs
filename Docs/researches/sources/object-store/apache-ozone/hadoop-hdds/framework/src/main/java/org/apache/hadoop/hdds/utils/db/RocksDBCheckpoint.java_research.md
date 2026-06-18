# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/RocksDBCheckpoint.java

## Purpose

`RocksDBCheckpoint` is a small `DBCheckpoint` value object for a RocksDB checkpoint directory plus snapshot metadata. The complete 81-line source was read for this report.

## Important APIs, Types, and Functions

Constructors accept a checkpoint `Path`, or `Path`, timestamp, latest RocksDB sequence number, and creation duration. Implemented APIs are `getCheckpointLocation`, `getCheckpointTimestamp`, `getLatestSequenceNumber`, `checkpointCreationTimeTaken`, and `cleanupCheckpoint`.

## Control Flow

There is no complex control flow. Construction captures metadata; getters return the stored values; cleanup logs and recursively deletes the checkpoint directory.

## State and Persistence Behavior

The object represents an on-disk RocksDB checkpoint directory. `cleanupCheckpoint()` permanently deletes that directory with Apache Commons `FileUtils.deleteDirectory`. It does not create checkpoints itself; creation is handled by `RocksDatabase.RocksCheckpoint` and higher-level DB store code.

## Dependencies and Integration Points

It implements `DBCheckpoint`, uses `Path`, `FileUtils`, `jakarta.annotation.Nonnull`, and SLF4J. It is returned to consumers that need snapshot location, sequence number, and cleanup responsibility.

## Risks and Edge Cases

Cleanup is destructive and assumes the path is a checkpoint directory. The one-argument constructor leaves latest sequence number at `-1` and creation duration at `0`, so callers must tolerate unknown metadata. IO failures propagate from delete.

## Test Signals

Tests should verify getter values, default metadata values, cleanup of a temporary directory, and propagation when deletion fails or the path is invalid.
