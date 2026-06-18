# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/HashLinkedListMemTableConfig.java

Purpose: Java `MemTableConfig` for hash linked-list memtable representation, requiring a prefix extractor for intended behavior. It configures fixed bucket count, huge page TLB size, bucket-entry logging threshold, whether to log bucket distribution at flush, and threshold to fall back/use skiplist.

Control flow is Java-side mutable configuration with defaults, fluent setters/getters, and native factory creation through `newMemTableFactoryHandle(...)`. State is stored in Java fields until the memtable factory handle is requested by options. Dependencies include `MemTableConfig`, prefix-extractor option APIs, and native memtable factory code.

Risks: without a prefix extractor RocksDB falls back to skiplist and logs a warning; defaults include a typo constant `DEFAUL_THRESHOLD_USE_SKIPLIST`; large bucket counts or huge pages affect memory; native factory receives current field values only at creation time. Tests should verify defaults, setters, factory creation, prefix-extractor integration, and fallback behavior when prefix extraction is absent.
