# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/SliceTest.java

## Purpose

This file validates the Java `Slice` wrapper used to pass byte ranges to native RocksDB APIs. It covers string and byte-array construction, offset construction, clearing, prefix removal, equality/hash code, prefix checks, and string conversion.

## Important APIs and types

The primary type is `Slice`. Tests use constructors from `String`, full `byte[]`, and `byte[]` plus offset, along with `empty`, `size`, `data`, `clear`, `removePrefix`, `startsWith`, `equals`, `hashCode`, `toString`, and `toString(true)`.

## Control flow

Each test creates one or more slices in try-with-resources, calls a small set of methods, and asserts byte or string output. `sliceClear` calls `clear()` twice to verify idempotent cleanup behavior.

## State and persistence behavior

The file does not touch DB persistence. It tests native memory ownership and view mutation inside a `Slice`; `removePrefix` and `clear` change the slice-visible range.

## Dependencies and integration points

`Slice` is used by many RocksDB Java APIs, including read options, ranges, comparators, trace writers, and SST file writers/readers. Correct byte ownership is foundational for JNI safety.

## Risks and test signals

Risks include double-free on clear, incorrect offset slicing, equality/hash mismatch, and lossy string conversion. Signals are exact data, size, string, equality, and prefix assertions.
