# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/SstPartitionerFixedPrefixFactory.java

## Purpose
`SstPartitionerFixedPrefixFactory` creates a native SST partitioner factory that partitions SST output by a fixed-length key prefix.

## Important APIs and Types
The public constructor takes `prefixLength`, calls `newSstPartitionerFixedPrefixFactory0`, and inherits the handle contract from `SstPartitionerFactory`. `disposeInternal` releases the native factory through JNI.

## Control Flow
Construction delegates allocation to native code. Disposal delegates native cleanup. Actual partition decisions happen in C++.

## State and Persistence Behavior
The Java object owns only the factory handle. Prefix length is not retained in Java after construction; native state owns it.

## Dependencies and Integration Points
It depends on `SstPartitionerFactory`, `RocksObject`, and JNI. It is meant to be attached to column-family configuration that controls SST writing and compaction output.

## Risks and Test Signals
Tests should validate zero/negative/large prefix lengths, option serialization into native column-family options, and whether generated SST boundaries match fixed prefixes. Since Java does not validate input, native validation is the safety boundary.
