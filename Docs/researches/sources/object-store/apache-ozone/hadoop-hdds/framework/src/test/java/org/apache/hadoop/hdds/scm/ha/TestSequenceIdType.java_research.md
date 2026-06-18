# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSequenceIdType.java

## Purpose

This class protects `SequenceIdType` enum names because they are persisted RocksDB keys.

## Important APIs, Types, And Functions

`testStringSyncWithEnumConstants()` asserts exact enum `name()` strings, including the deprecated or unusual casing `CertificateId`. `testIfNewEnumConstantGetsAdded()` compares the current enum set against an expected set and emits a compatibility-focused failure message.

## Control Flow

Tests enumerate constants, compute added/removed names relative to expected, and fail if any change is detected.

## State And Persistence

There is no runtime mutable state. The state being protected is persisted sequence-id key names in RocksDB.

## Dependencies And Integration Points

The file integrates with SCM HA sequence ID storage and any code that reads/writes counters keyed by `SequenceIdType.name()`.

## Risks

Any intentional enum addition/removal or rename requires explicit backward-compatibility analysis and test update. The guard does not verify database migration logic directly.

## Test Signals

Signals are exact enum-name equality and empty added/removed sets.
