# Research: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/BloomFilter.java

- **Purpose:** Java wrapper for RocksDB's built-in Bloom filter policy.
- **Important APIs/types/functions:** Extends `Filter`; default constructor uses 10 bits/key; public constructor creates native filter with a configurable bits/key; package constructor wraps an existing handle; deprecated two-argument constructor ignores block-based mode; `equals`/`hashCode` compare recorded `bitsPerKey`; JNI hook is `createNewBloomFilter(double)`.
- **Control flow:** Construction creates or wraps a native filter handle and stores the bits/key value for Java equality. The obsolete mode argument is ignored and delegates to the current constructor.
- **State and persistence behavior:** Native filter policy affects SST filter generation and read behavior when installed in a table config. Java records only the bits/key for equality; the native handle is owned through `Filter`.
- **Dependencies:** Depends on `Filter`, `Objects`, and native filter creation.
- **Integration points:** Commonly passed to `BlockBasedTableConfig.setFilterPolicy()` and then to `ColumnFamilyOptions`.
- **Risks:** Equality ignores native handle identity and any future filter parameters besides bits/key. Custom comparators that ignore key bytes must not use this filter unless semantics match. The filter must outlive table/options/users referencing it.
- **Test signals:** Native filter creation, default bits/key, equality/hash code, obsolete constructor behavior, and database reads with Bloom-filter-enabled table config.
