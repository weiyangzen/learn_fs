# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/DirectSliceTest.java

## Purpose

Tests `DirectSlice`, a Java wrapper for native slices backed by direct buffers or strings.

## Important APIs, control flow, and dependencies

The suite constructs `DirectSlice` from strings, direct `ByteBuffer`s, and direct buffers with explicit length. It calls `toString`, `get`, `removePrefix`, and `clear`, and verifies heap `ByteBuffer` inputs are rejected.

## State, persistence, risks, and test signals

No DB state is involved. The state is native/direct memory ownership and slice view offsets. Risks include accepting non-direct buffers, double free on repeated `clear`, incorrect null-termination handling, and prefix offset errors. Signals are expected strings/bytes and `IllegalArgumentException` for heap buffers.
