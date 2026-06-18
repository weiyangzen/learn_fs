# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/SstFileWriterTest.java

## Purpose

This suite tests Java external SST generation and ingestion. It covers writer operation overloads, direct-buffer writes, Java and native comparators, file-size reporting, ingestion into default and custom column families, and merge/delete semantics after ingestion.

## Important APIs and types

Key types are `SstFileWriter`, `EnvOptions`, `Options`, `StringAppendOperator`, `ComparatorOptions`, `BytewiseComparator`, `Slice`, `ByteBuffer`, `IngestExternalFileOptions`, `RocksDB`, and column-family descriptors/handles. `KeyValueWithOp` enumerates put, merge, delete, and direct-buffer operations.

## Control flow

`newSstFile` configures options, optionally installs a Java comparator, opens a temp SST file, applies each modeled operation through the matching writer overload, asserts direct-buffer position/limit mutation, finishes the file, and asserts nontrivial file size. Tests then either just generate files or ingest them into a DB/CF and read back values.

## State and persistence behavior

The writer persists an external SST file, and ingestion imports it into RocksDB state. Merge operands are resolved through `StringAppendOperator`, and delete records should produce missing keys.

## Dependencies and integration points

The file tests Java-to-native external file creation, comparator callbacks, direct-buffer transfer, file ingestion, and CF-specific ingestion options.

## Risks and test signals

Risks include comparator lifetime bugs, unsorted external file output, direct-buffer position mistakes, and ingestion mishandling of deletes/merges. Signals include file-size assertions and exact DB readback after ingestion.
