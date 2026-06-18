# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/TransactionOptionsTest.java

## Purpose

This suite verifies Java getter/setter bindings for per-transaction `TransactionOptions`.

## Important APIs and types

It uses `TransactionOptions` and `PlatformRandomHelper`.

## Control flow

Each test constructs options, sets one boolean or long field, and checks the getter. Covered fields are snapshot creation, deadlock detection, lock timeout, expiration, deadlock detection depth, and maximum write-batch size.

## State and persistence behavior

Only native option state is mutated. No transaction DB or persisted data is created.

## Dependencies and integration points

These options are consumed by `TransactionDB.beginTransaction`; this file validates Java-to-native option marshaling before integration tests use them.

## Risks and test signals

Risks include bool/long conversion errors and field mapping drift. Signals are exact round-trip equality.
