# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/WALRecoveryModeTest.java

## Purpose

This file tests enum value mapping for `WALRecoveryMode`.

## Important APIs and types

It uses `WALRecoveryMode.values()`, `getValue()`, and `getWALRecoveryMode(int)`.

## Control flow

The single test iterates every enum constant, converts it to its integer value, maps that value back to an enum, and asserts identity.

## State and persistence behavior

There is no DB state. The tested state is the static enum mapping table.

## Dependencies and integration points

This guards Java option decoding for WAL recovery mode values passed to or from native code.

## Risks and test signals

Risks include enum ordinal/value drift and missing mapping for new modes. The signal is exact round-trip equality for every constant.
