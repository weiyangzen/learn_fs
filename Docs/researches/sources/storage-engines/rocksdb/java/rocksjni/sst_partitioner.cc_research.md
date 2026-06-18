<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/sst_partitioner.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/sst_partitioner.cc

Purpose: Exposes `NewSstPartitionerFixedPrefixFactory` to Java.

Important APIs/types/functions: `newSstPartitionerFixedPrefixFactory0` creates a `std::shared_ptr<SstPartitionerFactory>` from a prefix length and returns a native handle. `disposeInternalJni` deletes the shared pointer wrapper.

Control flow: Java passes a prefix length, C++ creates the fixed-prefix factory, and options code can consume the returned shared pointer. Disposal releases the wrapper.

State and persistence behavior: The factory is process-local configuration. It affects how RocksDB partitions generated SSTs but does not persist state by itself.

Dependencies and integration points: Depends on `rocksdb/sst_partitioner.h`, generated `org_rocksdb_SstPartitionerFixedPrefixFactory.h`, and pointer conversion helpers. The returned factory integrates with table/compaction options.

Risks: The source comment says SstFileManager, but the code is for SstPartitioner. Prefix length is not validated in JNI; invalid values rely on RocksDB factory behavior. Handle misuse can crash.

Test signals: Tests should install the factory in options, write data with varying prefixes, verify partition behavior where observable, and check repeated create/dispose cycles.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/sst_partitioner.cc -->
