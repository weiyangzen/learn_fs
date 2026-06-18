# sources/storage-engines/leveldb/util/hash.cc

## Purpose
`hash.cc` implements LevelDB's internal non-cryptographic hash.

## Important APIs, Types, and Functions
`Hash(const char* data, size_t n, uint32_t seed)` is the exported function. It uses `DecodeFixed32` and a fallback `FALLTHROUGH_INTENDED` annotation.

## Control Flow
The hash initializes from seed and length, consumes four bytes at a time with a Murmur-like multiply/xor mix, then folds one to three trailing bytes through fallthrough cases.

## State, Persistence, and Integration
No mutable state. The function is used by cache shard/table lookup, Bloom filters, and tests. Hash outputs affect in-memory distribution and persisted Bloom filter bits.

## Risks and Test Signals
Unsigned byte handling for high-bit bytes is critical and explicitly tested. Changing the algorithm breaks Bloom filter compatibility for existing tables.
