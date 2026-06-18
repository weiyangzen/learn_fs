# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/SstFileReaderTest.java

## Purpose

This parameterized suite verifies Java `SstFileReader` and `SstFileReaderIterator` behavior for externally generated SST files, using both direct and heap `ByteBuffer` allocators.

## Important APIs and types

The file uses `SstFileWriter` to create input files, `SstFileReader`, `SstFileReaderIterator`, `ReadOptions`, `TableProperties`, `Options`, `EnvOptions`, `StringAppendOperator`, `Slice`, and `ByteBufferAllocator`. The helper `KeyValueWithOp` models SST operations.

## Control flow

`newSstFile` writes three ordered key/value records using `SstFileWriter`, then `readSstFile` opens the file, creates an iterator, verifies checksum and table properties, reads keys/values, and tests `seek`/`seekForPrev` with whole and sliced buffers.

## State and persistence behavior

The persisted artifact is a temporary `.sst` file. It is not ingested into a DB. The reader opens immutable on-disk table state and exposes iterator state over it.

## Dependencies and integration points

This test links Java external SST writing and reading, table property exposure, checksum verification, and buffer marshalling across JNI.

## Risks and test signals

Risks include reader incompatibility with writer output, bad buffer position handling, missed checksum failures, and property conversion errors. Signals are checksum success, `numEntries == 3`, exact key/value reads, and correct seek boundary behavior.
