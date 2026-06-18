# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/DBCheckpoint.java

## Purpose
`DBCheckpoint` is the generic contract for filesystem-backed snapshots of an HDDS database.

## Important APIs and Types
It exposes checkpoint location, creation timestamp, latest sequence number, checkpoint creation duration, and `cleanupCheckpoint()`.

## Control Flow and State
The interface has no implementation. Implementations such as RocksDB checkpoints own the snapshot directory and cleanup behavior.

## Persistence, Dependencies, and Integration
It represents persisted checkpoint artifacts on local disk and is used by checkpoint managers, snapshot providers, and checkpoint streaming utilities.

## Risks and Test Signals
Implementations must define whether cleanup is destructive, idempotent, and safe under concurrent readers. Tests should verify timestamp/sequence accuracy, cleanup behavior, missing-path handling, and integration with tar streaming and HA installation flows.
