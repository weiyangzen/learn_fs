<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/thread_status.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/thread_status.cc

Purpose: Bridges Java `ThreadStatus` helper methods to C++ `ROCKSDB_NAMESPACE::ThreadStatus` static formatting and interpretation APIs.

Important APIs/types/functions: Methods expose thread type name, operation name, microsecond formatting, operation stage name, operation property name, operation property interpretation, and state name. Enum conversion helpers map Java bytes to C++ enum values.

Control flow: Simple name methods convert enum bytes, call `ThreadStatus` static methods, and convert strings back to Java. `interpretOperationProperties` copies a Java `long[]` into a `uint64_t[]`, calls `InterpretOperationProperties`, and converts the resulting map to Java.

State and persistence behavior: Stateless conversion only. No DB or persistent state is touched.

Dependencies and integration points: Includes `rocksdb/thread_status.h`, generated `org_rocksdb_ThreadStatus.h`, and `portal.h` for enum and map/string conversion.

Risks: `interpretOperationProperties` assumes the Java array has the expected length for the operation type; RocksDB interpretation may read required positions from the provided pointer. Enum conversion correctness depends on generated Java constants. Large unsigned properties may be sign-represented as Java longs.

Test signals: Tests should verify enum name mappings, microsecond formatting, property names by operation/index, interpreted property maps for known arrays, and invalid enum/short-array handling.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/thread_status.cc -->
