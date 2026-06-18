# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/FilterPolicyType.java

Purpose: enum for filter policy types used with block-based tables: unknown, bloom, and ribbon.

Control flow exposes byte values and has `createFilter(long, double)`, which currently constructs a `BloomFilter` only for `kBloomFilterPolicy`; other values return null. State is immutable; native filter handles and parameters are handled by concrete filters. Dependencies include `Filter`, `BloomFilter`, and block-based table options.

Risks: returning null for ribbon/unknown requires callers to handle unsupported creation; byte values must match native; creation semantics assume the passed handle is suitable for `BloomFilter`. Tests should verify bytes, bloom creation, non-bloom null behavior, and integration with block table filter options.
