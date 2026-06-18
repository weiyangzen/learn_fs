# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/fs/MockSpaceUsagePersistence.java

## Purpose

This utility supplies an in-memory `SpaceUsagePersistence` implementation backed by an `AtomicLong`, used to test cached usage loading and saving without files.

## Important APIs, Types, And Functions

`inMemory(AtomicLong)` returns a private `Memory` instance. `Memory.load()` returns `OptionalLong.of(target.get())`; `Memory.save(SpaceUsageSource)` writes `source.getUsedSpace()` into the target.

## Control Flow

Tests pass an `AtomicLong` representing persisted state into `inMemory`, use it in `SpaceUsageCheckParams`, then inspect whether production code loaded or saved the expected value.

## State And Persistence

State lives in the caller-provided `AtomicLong`. It is memory-only persistence, thread-safe at the scalar operation level, and has no expiry or validation logic.

## Dependencies And Integration Points

It implements production `SpaceUsagePersistence` and reads from production `SpaceUsageSource`.

## Risks

Because `load()` always returns a present value, an initial zero represents a present zero, not missing persistence. Tests for missing persisted values must avoid this helper or use production/file persistence semantics.

## Test Signals

Useful signals include assertions that startup reads the atomic value and shutdown/save writes the latest used-space value.
