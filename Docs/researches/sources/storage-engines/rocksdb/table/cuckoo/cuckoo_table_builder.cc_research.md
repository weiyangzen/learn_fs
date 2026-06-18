# sources/storage-engines/rocksdb/table/cuckoo/cuckoo_table_builder.cc

Purpose: implements the writer for RocksDB cuckoo-table SSTs, optimized for fast point lookups with fixed-length keys/values and limited operation types.

Important APIs/types/functions: defines cuckoo table property names and magic number, then implements `CuckooTableBuilder` constructor, `Add`, `Finish`, `Abandon`, `NumEntries`, `FileSize`, `MakeHashTable`, `MakeSpaceForKey`, `GetFileChecksum`, and checksum function name accessors. Internal helpers expose stored keys/values and detect deletion records after closure.

Control flow: `Add` parses internal keys, accepts only value/deletion types, determines last-level mode from first key sequence number, enforces fixed key/value lengths, stores values and deletions in separate contiguous strings, tracks smallest/largest user keys for empty-bucket filler generation, and grows table size for power-of-two hashing. `Finish` computes module table size if needed, builds a cuckoo hash table, finds an unused key outside the observed bytewise range, writes all buckets with empty fillers, writes properties and metaindex blocks, then appends a footer. `MakeHashTable` tries direct candidate buckets and uses `MakeSpaceForKey` BFS displacement; it increases hash function count up to the configured maximum.

State and persistence: persisted layout is a flat bucket array followed by properties block, metaindex block, and footer. Properties include empty key, hash function count, table size, value length, last-level flag, cuckoo block size, identity/module hash flags, and user key length.

Dependencies/integration: depends on internal key parsing, `WritableFileWriter`, block/property/metaindex builders, `CuckooHash`, table properties, and footer builder.

Risks and test signals: risks include duplicate user-key detection via comparator, fixed-size assumptions, undefined/unaligned identity hash reads, empty-key search failure, collision-path limits, and partial files on finish errors. Tests cover empty files, collisions, displacement paths, block-size probing, deletions, duplicate keys, and too-long collision paths.
