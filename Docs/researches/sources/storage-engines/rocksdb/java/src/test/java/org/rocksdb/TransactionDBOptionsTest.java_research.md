# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/TransactionDBOptionsTest.java

## Purpose

This suite verifies Java getter/setter bindings for `TransactionDBOptions`.

## Important APIs and types

It uses `TransactionDBOptions`, `TxnDBWritePolicy`, and `PlatformRandomHelper` for generated long values.

## Control flow

Each test constructs options, sets one field, and asserts the getter returns the same value. Covered fields are maximum locks, stripe count, transaction lock timeout, default lock timeout, and write policy.

## State and persistence behavior

State is only native option configuration. No DB is opened and no persisted data is created.

## Dependencies and integration points

The suite verifies JNI marshaling for transaction DB option fields that later influence lock-table sizing, timeout behavior, and write policy.

## Risks and test signals

Risks include signed long conversion mistakes, wrong native field mapping, and enum mapping drift. Signals are exact round-trip equality.
