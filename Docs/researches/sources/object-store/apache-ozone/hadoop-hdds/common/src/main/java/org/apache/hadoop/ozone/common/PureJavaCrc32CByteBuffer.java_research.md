# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/PureJavaCrc32CByteBuffer.java

## Purpose

`PureJavaCrc32CByteBuffer` is the CRC-32C counterpart of `PureJavaCrc32ByteBuffer`. It keeps a table-backed `mod(long)` helper after removal of older `ChecksumByteBuffer` update behavior.

## APIs and control flow

The only public API is `mod(long x)`. It computes `x mod p` for the CRC-32C polynomial by XORing the high 32 bits with four table lookups derived from the low 32-bit value's bytes. The table is generated for polynomial `0x82F63B78`, with a note preserving Intel BSD-license attribution for portions of the file.

## State, dependencies, and integration

The class has no mutable state and no external dependencies. It integrates with CRC-32C checksum combination or validation code that needs polynomial modular reduction.

## Risks and test signals

Correctness depends entirely on the static table and byte-index expression. Regression tests should compare `mod(long)` to independent CRC-32C polynomial calculations, include high-bit and zero cases, and protect the table from accidental reformatting or truncation.
