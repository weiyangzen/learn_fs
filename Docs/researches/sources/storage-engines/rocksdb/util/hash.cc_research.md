# sources/storage-engines/rocksdb/util/hash.cc

Purpose: implementation of RocksDB common non-cryptographic hash functions, including legacy 32-bit MurmurHash1, XXH3-based 64/128-bit hashes, slice-part hashing, and bijective 128-bit mixing/unmixing helpers.

Important APIs/functions: `Hash()` implements persistent 32-bit MurmurHash1-compatible hashing. `Hash64()` delegates to `XXPH3_64bits(_withSeed)`. `GetSlicePartsNPHash64()` concatenates slice parts and hashes them. `Hash128()` wraps XXH3 128-bit output into `Unsigned128`. `Hash2x64()` returns high/low 64-bit halves. `BijectiveHash2x64()` and `BijectiveUnhash2x64()` implement invertible 128-bit transformations adapted from XXH3 small-input mixing. `kGetSliceNPHash64UnseededFnPtr` is initialized to `GetSliceHash64`.

Control flow: `Hash()` processes 4-byte little-endian chunks, then a switch over 0-3 trailing bytes using `int8_t` casts to preserve legacy sign-extension behavior without UB. 64/128-bit functions call xxhash variants. Bijective hash/unhash uses fixed secrets, multiplication to/from 128-bit, endian swaps, avalanche/unavalanche, and modular inverse constants.

State and persistence: persistent hash functions define stable values used in formats/data structures; comments distinguish stable `Hash64`/`Hash` from non-persistent wrappers in the header. Global function pointer is process state.

Dependencies and integration: depends on `coding`, `hash128.h`, `math128.h`, `xxhash`, `xxph3`, and `port/lang.h`. Used by Bloom filters, cache/hash containers, partitioning, and benchmarks.

Risks: legacy 32-bit behavior intentionally preserves signed-char quirks; changing it would break persistent compatibility. `GetSlicePartsNPHash64()` copies all parts and can allocate. Seed sequences differing by one may not be independent.

Test signals: no direct hash test in this subset; dynamic Bloom and filter benchmark exercise hash use indirectly.
