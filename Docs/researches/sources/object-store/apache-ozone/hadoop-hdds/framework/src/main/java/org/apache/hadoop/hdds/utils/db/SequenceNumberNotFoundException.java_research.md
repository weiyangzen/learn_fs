# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/SequenceNumberNotFoundException.java

## Purpose

`SequenceNumberNotFoundException` signals that requested RocksDB WAL/update data cannot be found for a sequence number. The complete 35-line source was read for this report.

## Important APIs, Types, and Functions

It extends `IOException` and provides a no-argument constructor and a message constructor.

## Control Flow

There is no internal control flow. Higher-level WAL delta or checkpoint code throws/catches it as an I/O condition.

## State and Persistence Behavior

The class owns no state beyond inherited exception message/cause fields. It reflects WAL retention or sequence availability in persistent RocksDB state.

## Dependencies and Integration Points

It depends only on `java.io.IOException`. It integrates conceptually with `RocksDatabase.getUpdatesSince` and DB checkpoint/delta replication paths.

## Risks and Edge Cases

It has no cause-taking constructor, so callers that need to preserve an underlying cause must wrap differently or use `initCause`.

## Test Signals

Tests are usually indirect through update-since/checkpoint code; direct tests can verify checked-exception typing and message propagation.
