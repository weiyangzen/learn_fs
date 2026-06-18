# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/SstPartitionerTest.java

## Purpose

This file tests the Java binding for `SstPartitionerFixedPrefixFactory`, ensuring compaction output can be partitioned by fixed key prefix for default and custom column families.

## Important APIs and types

The suite uses `SstPartitionerFixedPrefixFactory`, `Options.setSstPartitionerFactory`, `ColumnFamilyOptions.setSstPartitionerFactory`, `RocksDB`, `FlushOptions`, `compactRange`, and `LiveFileMetaData`.

## Control flow

Each test writes keys with two different four-byte prefixes across two flushes, compacts, then inspects live file metadata. The custom-CF variant creates a column family with the partitioner installed in its options.

## State and persistence behavior

The DB creates SST files through flush and compaction. The expected durable state after compaction is two live files, reflecting partitioned output by prefix.

## Dependencies and integration points

This test integrates Java option wiring with the C++ SST partitioner factory and compaction output generation.

## Risks and test signals

Risks include partitioner factory lifetime issues, CF option misapplication, and compaction output shape changes. The main signal is `getLiveFilesMetaData().size() == 2`.
