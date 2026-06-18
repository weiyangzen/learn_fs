# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/Filter.java

Purpose: abstract native-backed base class for filter policies, such as Bloom filters, used by table options.

Control flow stores the native handle in `RocksObject`; `disposeInternal()` delegates to handle-based disposal, which calls native `disposeInternalJni`. Concrete subclasses supply construction and behavior. State is native filter-policy configuration; Java does not persist it directly, but table options can persist filter metadata in SSTs.

Dependencies include `RocksObject`, concrete filters like `BloomFilter`, and `FilterPolicyType`. Risks center on native ownership and ensuring subclasses use correct handles. Tests should create/dispose concrete filters, attach them to block-based table options, read/write data to exercise filter construction, and verify no double free when filters are shared or option objects are disposed.
