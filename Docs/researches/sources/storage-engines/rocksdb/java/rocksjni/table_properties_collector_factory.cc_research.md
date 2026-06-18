<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/table_properties_collector_factory.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/table_properties_collector_factory.cc

Purpose: Bridges Java `TablePropertiesCollectorFactory` to RocksDB's compact-on-deletion table properties collector factory.

Important APIs/types/functions: `newCompactOnDeletionCollectorFactory` allocates `TablePropertiesCollectorFactoriesJniWrapper`, fills its shared pointer with `NewCompactOnDeletionCollectorFactory(sliding_window_size, deletion_trigger, deletion_ratio)`, and returns the wrapper pointer. `deleteCompactOnDeletionCollectorFactory` deletes the wrapper.

Control flow: Java creates a factory with compaction-on-deletion thresholds, passes the handle into options code, then calls delete when done. The wrapper exists because Java needs a stable pointer to a shared pointer field.

State and persistence behavior: The collector factory is in-memory configuration that affects table property collection and compaction decisions when RocksDB builds tables. It does not directly persist data, but generated table properties become part of SST metadata.

Dependencies and integration points: Includes its local header, generated `org_rocksdb_TablePropertiesCollectorFactory.h`, pointer conversion, `rocksdb/db.h`, and `rocksdb/utilities/table_properties_collectors.h`. Options code must understand `TablePropertiesCollectorFactoriesJniWrapper`.

Risks: The local header path uses `java/rocksjni/...`, unlike many neighboring includes that use `rocksjni/...`; build include roots must support this. The delete function does not null-check handles. Threshold values are not validated in JNI.

Test signals: Tests should configure compact-on-deletion, write/delete workloads that trigger collected properties, verify factory disposal, and cover build/include portability.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/table_properties_collector_factory.cc -->
