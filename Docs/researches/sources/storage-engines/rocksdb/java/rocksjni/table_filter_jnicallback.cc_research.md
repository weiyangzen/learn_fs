<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/table_filter_jnicallback.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/table_filter_jnicallback.cc

Purpose: Implements the C++ callback adapter that lets RocksDB invoke a Java `AbstractTableFilter`.

Important APIs/types/functions: `TableFilterJniCallback::TableFilterJniCallback` resolves `AbstractTableFilterJni::getFilterMethod` and creates `m_table_filter_function`. `GetTableFilterFunction` returns the stored `std::function<bool(const TableProperties&)>`.

Control flow: When RocksDB calls the function, the adapter attaches/obtains a thread-local `JNIEnv`, converts C++ `TableProperties` to a Java object, invokes the Java boolean filter method, describes any exception to stderr, releases the JNI environment if attached, and returns false on conversion/call failure.

State and persistence behavior: Stores method ID and Java callback reference inherited from `JniCallback`. No persistent state is written. The return value influences whether RocksDB includes/excludes table data in operations using the filter.

Dependencies and integration points: Depends on `table_filter_jnicallback.h` and `portal.h`, including `TablePropertiesJni` and `AbstractTableFilterJni`. Created by `table_filter.cc` and often passed into DB table-property APIs/options.

Risks: On the success path the local `jtable_properties` reference is not explicitly deleted before returning, which can pressure local reference tables if invoked repeatedly on an attached thread. Exceptions are described and swallowed as `false`, so Java errors may become silent filtering behavior rather than propagated operation failures. Method ID lookup failure leaves the object in a partially initialized state.

Test signals: Tests should force callback success, callback false, Java exception, and high-volume invocation to detect local-reference leaks. Threaded tests should validate attach/release behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/table_filter_jnicallback.cc -->
