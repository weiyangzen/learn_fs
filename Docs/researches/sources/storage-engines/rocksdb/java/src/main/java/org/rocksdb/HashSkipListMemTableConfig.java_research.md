# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/HashSkipListMemTableConfig.java

Purpose: Java `MemTableConfig` for hash skip-list memtable representation. It configures bucket count, skip-list height, branching factor, and huge page TLB size.

Control flow is Java-side mutable configuration initialized with defaults. Fluent setters update fields, getters return current values, and the native memtable factory handle is created from those fields. State persists only in the config object until installed into column-family options; native RocksDB owns runtime memtables. Dependencies include `MemTableConfig`, prefix-extractor options, and native hash skip-list factory.

Risks: like hash linked-list, this representation depends on prefix extraction; invalid height/branching/bucket values are not Java-validated; huge page settings are platform-sensitive. Tests should cover default values, setter/getters, native factory creation, DB open/write behavior with prefix extractor, and fallback/warning behavior without one.
