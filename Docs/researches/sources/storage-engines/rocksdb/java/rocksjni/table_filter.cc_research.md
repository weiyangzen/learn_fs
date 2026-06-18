<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/table_filter.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/table_filter.cc

Purpose: Constructs native `TableFilterJniCallback` objects for Java `AbstractTableFilter`.

Important APIs/types/functions: `Java_org_rocksdb_AbstractTableFilter_createNewTableFilter` allocates `ROCKSDB_NAMESPACE::TableFilterJniCallback(env, jtable_filter)` and returns the native pointer.

Control flow: Java subclass creation calls this function; C++ creates a callback wrapper that stores method IDs and a global callback reference through `JniCallback`.

State and persistence behavior: The callback is native process state. It influences RocksDB table filtering decisions during operations that accept table filters but does not persist data.

Dependencies and integration points: Includes generated `org_rocksdb_AbstractTableFilter.h`, pointer conversion helpers, and `table_filter_jnicallback.h`. Disposal is through `RocksCallbackObject` base handling.

Risks: Lifetime must cover any RocksDB background or iterator use of the filter. Constructor exceptions leave a returned object with possibly missing method IDs unless Java checks pending exceptions.

Test signals: Tests should install a Java table filter, assert it receives table properties, verify true/false decisions affect table selection, and validate disposal through the callback base.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/table_filter.cc -->
