<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/remove_emptyvalue_compactionfilterjni.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/remove_emptyvalue_compactionfilterjni.cc

Purpose: Exposes RocksDB's `RemoveEmptyValueCompactionFilter` utility to Java.

Important APIs/types/functions: `Java_org_rocksdb_RemoveEmptyValueCompactionFilter_createNewRemoveEmptyValueCompactionFilter0` allocates `ROCKSDB_NAMESPACE::RemoveEmptyValueCompactionFilter` and returns its pointer with `GET_CPLUSPLUS_POINTER`.

Control flow: There is a single constructor bridge. Java calls it, C++ allocates the filter, and Java stores the returned handle for use in compaction filter configuration.

State and persistence behavior: The native filter is stateless except for C++ object lifetime. Its effect is persistent only when RocksDB compaction applies it and removes entries whose values are empty.

Dependencies and integration points: Depends on generated `org_rocksdb_RemoveEmptyValueCompactionFilter.h`, `utilities/compaction_filters/remove_emptyvalue_compactionfilter.h`, and JNI pointer conversion. It integrates with compaction filter ownership/disposal logic elsewhere in RocksJNI.

Risks: This file has no disposal entry point, so correctness depends on the Java class hierarchy or another native base disposer deleting the returned filter. A missing disposal path would leak the filter. The bridge performs no error handling because `new` failures surface as native allocation failure rather than a RocksDB `Status`.

Test signals: Tests should configure this filter, compact a DB containing empty and non-empty values, and verify only empty-value keys are removed. Native leak checks should cover repeated create/dispose cycles through the Java wrapper.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/remove_emptyvalue_compactionfilterjni.cc -->
