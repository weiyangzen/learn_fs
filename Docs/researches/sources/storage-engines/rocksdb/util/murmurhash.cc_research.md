# sources/storage-engines/rocksdb/util/murmurhash.cc

Purpose: contains RocksDB's copy of MurmurHash2-family implementations selected by architecture: 64-bit MurmurHash64A on x86_64, 32-bit MurmurHash2 on i386, and endian/alignment-neutral MurmurHashNeutral2 elsewhere.

Important APIs/types/functions: implements `MurmurHash64A(const void*, int, unsigned int)`, `MurmurHash2(const void*, int, unsigned int)`, or `MurmurHashNeutral2(const void*, int, unsigned int)` depending on compile target. All use Murmur constants, tail-byte switch statements with intentional fallthrough, and final avalanche mixes.

Control flow: each function initializes the hash from seed and length, processes full machine words or manually assembled 32-bit words, handles remaining tail bytes with a fallthrough switch, and applies final xor/multiply/xor mixing before returning the hash.

State and persistence behavior: stateless pure hash functions. Output width and exact values are architecture-dependent by design through the header macro selection, so persisted users must account for the selected build target if values cross platforms.

Dependencies/integration points: includes `murmurhash.h` and `port/lang.h` for fallthrough annotations. The header exposes `MurmurHash`, `MURMUR_HASH`, `murmur_t`, and a `Slice` hasher, making this implementation available to hash containers and utility code.

Risks: x86_64 and i386 paths perform unaligned word loads and are endian-sensitive, matching original MurmurHash caveats. UBSAN alignment suppression is applied for x86_64 in sanitizer builds. `len` is `int`, so callers must avoid sizes outside that range. The neutral path is slower but safer for strict-alignment or non-little-endian platforms.

Test signals: no dedicated MurmurHash test in this subset. Broader hash stability is covered in `hash_test.cc` for other hash APIs, while Murmur-specific confidence depends on consumers and the original algorithm contract.
