# Research: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/BuiltinComparator.java

- **Purpose:** Public enum selecting RocksDB built-in key comparators from Java.
- **Important APIs/types/functions:** Values are `BYTEWISE_COMPARATOR` and `REVERSE_BYTEWISE_COMPARATOR`.
- **Control flow:** No methods; `ColumnFamilyOptions.setComparator(BuiltinComparator)` passes `ordinal()` to native code.
- **State and persistence behavior:** Stateless enum. Selection affects on-disk key ordering and must remain stable for a database's lifetime.
- **Dependencies:** Used by `ColumnFamilyOptions`; no direct imports.
- **Integration points:** Database and column-family creation options.
- **Risks:** Native mapping currently relies on ordinal order, so reordering enum constants would be a compatibility bug. Changing comparator after database creation is not allowed by RocksDB semantics.
- **Test signals:** Opening DB/CFs with each comparator and verifying native order/mapping.
