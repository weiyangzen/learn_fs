# sources/storage-engines/rocksdb/util/murmurhash.h

Purpose: declares the architecture-selected MurmurHash API and provides a RocksDB `Slice` functor for using MurmurHash in hash-based containers.

Important APIs/types/functions: compile-time branches define `MURMUR_HASH`, `MurmurHash`, and `murmur_t`. On x86_64 they map to `uint64_t MurmurHash64A`; on i386 to `unsigned int MurmurHash2`; otherwise to `unsigned int MurmurHashNeutral2`. `ROCKSDB_NAMESPACE::murmur_hash::operator()` hashes a `Slice` with seed zero and returns `size_t`.

Control flow: inclusion selects declarations and aliases through preprocessor architecture checks. The functor simply passes `slice.data()`, `static_cast<int>(slice.size())`, and seed `0` to the selected implementation.

State and persistence behavior: no state. Hash width varies by target architecture through `murmur_t`, and the functor truncates or widens to `size_t` as the platform dictates.

Dependencies/integration points: includes `<stdint.h>` and `rocksdb/slice.h`. The implementation is in `murmurhash.cc`; consumers include STL or custom hash tables needing `Slice` keys.

Risks: macro aliases can obscure which function is compiled on a given platform. `Slice::size()` is cast to `int`, so very large slices would overflow the API contract. Because algorithms differ by architecture, this should not be used for portable persisted hashes unless the platform is fixed.

Test signals: no direct test in this subset. Any behavior validation comes from consumers using `murmur_hash` plus architecture-specific build coverage.
