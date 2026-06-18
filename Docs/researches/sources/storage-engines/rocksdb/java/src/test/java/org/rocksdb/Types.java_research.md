# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/Types.java

## Purpose

This helper provides little-endian conversion utilities between Java `int` values and four-byte arrays for tests.

## Important APIs and types

It exposes static methods `byteToInt(byte[])` and `intToByte(int)`.

## Control flow

`byteToInt` masks each of the first four bytes with `0xff` and shifts them by 0, 8, 16, and 24 bits. `intToByte` emits the same byte order with unsigned shifts.

## State and persistence behavior

The class is stateless and has no persistence behavior.

## Dependencies and integration points

It has no external dependencies beyond Java primitive arrays. It is suitable for tests that need deterministic byte ordering.

## Risks and test signals

Risks include callers passing arrays shorter than four bytes and assuming big-endian order. There are no direct tests in this file; round-trip use in other tests would be the signal.
