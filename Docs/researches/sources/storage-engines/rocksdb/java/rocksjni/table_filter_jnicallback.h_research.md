<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/table_filter_jnicallback.h -->
# sources/storage-engines/rocksdb/java/rocksjni/table_filter_jnicallback.h

Purpose: Declares `TableFilterJniCallback`, the C++ holder for a Java table-filter callback.

Important APIs/types/functions: The class inherits `JniCallback`, exposes a constructor and `GetTableFilterFunction`, and stores a `jmethodID` plus a `std::function<bool(const TableProperties&)>`.

Control flow: The header defines the callback contract used by `table_filter_jnicallback.cc`. RocksDB receives the returned `std::function`; Java disposal treats the object as a `JniCallback`.

State and persistence behavior: Declares process-local callback state only.

Dependencies and integration points: Includes JNI, `<functional>`, `<memory>`, `rocksdb/table_properties.h`, and `rocksjni/jnicallback.h`.

Risks: The stored `std::function` captures `this`, so it must not outlive the callback object. No copy/move restrictions are declared, so accidental copying would duplicate a pointer-owning callback wrapper if ever used that way.

Test signals: Compile tests catch signature drift. Runtime tests should ensure functions obtained before disposal are not used after disposal and that Java callbacks work from non-Java RocksDB threads.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/table_filter_jnicallback.h -->
