# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/WalFilterTest.java

## Purpose

This suite verifies Java `AbstractWalFilter` integration during DB reopen/recovery and checks every `WalProcessingOption`.

## Important APIs and types

It uses `DBOptions.setWalFilter`, `AbstractWalFilter`, `WalProcessingOption`, `LogRecordFoundResult`, `WriteBatch`, column-family descriptors/handles, and test utilities for log-iterator options and dummy values.

## Control flow

For each processing option, the test writes three WAL batches to a DB, closes it, installs a `TestableWalFilter`, and reopens the DB. The filter records column-family log-number/name maps and log record metadata. On a configured record index it returns the tested processing option; otherwise it continues.

## State and persistence behavior

The DB writes durable WAL records, then recovery replays them through the filter. Filter state is Java-side lists/maps populated by native recovery callbacks. `CORRUPTED_RECORD` is the only option expected to allow a recovery exception path.

## Dependencies and integration points

This is a JNI callback test for WAL recovery, write-batch handoff to filters, column-family metadata maps, and processing-option conversion.

## Risks and test signals

Risks include unpinned filters, wrong option mapping, recovery exceptions for non-corrupt options, and missing log metadata. Signals are non-empty log number/name lists and the special exception handling for `CORRUPTED_RECORD`.
