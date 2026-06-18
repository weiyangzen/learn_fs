# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/TransactionLogIteratorTest.java

## Purpose

This suite validates Java access to RocksDB update logs through `TransactionLogIterator`.

## Important APIs and types

It uses `RocksDB.getUpdatesSince`, `TransactionLogIterator`, `TransactionLogIterator.BatchResult`, `Options.setWalTtlSeconds`, `Options.setWalSizeLimitMB`, `FlushOptions`, and column-family creation.

## Control flow

Tests construct an iterator from sequence zero, write batches of keys, flush, assert latest sequence numbers, and retrieve the first batch. One test advances to the end, writes another record, calls `next`, and verifies the iterator becomes valid again. Another closes/reopens the DB and iterates updates after restart.

## State and persistence behavior

The file relies on WAL persistence and sequence numbers. Flush does not erase the ability to query updates because WAL TTL/size limits are configured to retain logs.

## Dependencies and integration points

This exercises Java wrappers for transaction log iteration, WAL retention options, batch result conversion, sequence-number tracking, and restart recovery.

## Risks and test signals

Risks include iterator stalling at end, losing updates after restart/flush, wrong sequence numbering, and native iterator status propagation. Signals are validity transitions, `sequenceNumber() == 1`, and latest sequence-number equality.
