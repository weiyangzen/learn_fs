## sources/storage-engines/rocksdb/table/block_based/data_block_footer.h

Purpose: declares `DataBlockFooter`, the on-block trailer metadata for data block structure and features.

Important APIs/types: constants `kMaxNumRestarts`, `kMaxEncodedLength`, and `kMinEncodedLength` describe footer limits. Fields include `index_type`, `separated_kv`, `values_section_offset`, `num_restarts`, and `is_uniform`. Constructors support default binary-search/zero-restart state and explicit index type plus restart count. Methods are `EncodeTo()` and `DecodeFrom()`.

Control flow: block writers populate the fields before encoding; block readers decode from the end of the input slice and use the resulting metadata to locate restart arrays, values section, hash index, and uniform-search hints.

State and persistence behavior: the encoded footer stores low 28 bits of restart count plus high feature bits. With separated KV, an extra fixed32 offset precedes the packed word. The header documents compatibility expectations and why only some reserved bits can be safely interpreted by older versions as corruption.

Dependencies/integration points: depends on RocksDB `Slice`, `Status`, and table options. It is used by `BlockBuilder`, `Block`, and tests that compute raw block boundaries.

Risks: the restart-count capacity is tied to 32-bit block-size assumptions. New features must respect reserved-bit compatibility. Callers must handle variable encoded length rather than assuming four bytes.

Test signals: `block_test.cc` separated-KV corruption helpers use `kMaxNumRestarts` and footer-size logic; data block hash and uniformity tests exercise `index_type` and `is_uniform` bits through reader behavior.
