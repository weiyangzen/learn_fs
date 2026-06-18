# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/DataBlockIndexType.java

Purpose: enum for block-based table data block indexing: binary search only or binary plus hash.

Control flow is immutable byte exposure through package-visible `getValue()`. State is not Java-persisted but is sent through table option JNI and persisted in table/options metadata according to RocksDB behavior. Dependencies include `BlockBasedTableConfig` or equivalent block-based table option consumers.

Risks: byte values must match C++ `DataBlockIndexType`, and there is no reverse lookup in this file. Tests should verify option round-trips and table creation with hash indexing, including prefix-extractor requirements where applicable.
