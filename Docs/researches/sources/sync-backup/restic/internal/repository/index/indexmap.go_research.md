## sources/sync-backup/restic/internal/repository/index/indexmap.go

Purpose: custom memory-efficient chained hash table for mapping blob IDs to one or more index entries.

Important APIs/types: `indexMap` stores bucket heads, entry count, a maphash seed, and a `hashedArrayTree` block allocator. `add`, `values`, `valuesWithID`, `get`, `firstIndex`, `preallocate`, `hash`, `init`, `len`, `newEntry`, and `resolve` implement map behavior. Bloom helpers `bloomCleanID`, `bloomForID`, `bloomHasID`, and `bloomInsertID` encode a small bloom filter into upper bits of entry indices on 64-bit platforms. `indexEntry` stores blob ID, next pointer, pack index, offset, length, and uncompressed length. `hashedArrayTree` allocates stable entry addresses with growing block sizes.

Control flow and state: map initialization is lazy. `add` prepends to the bucket chain and stores bloom metadata. `preallocate` grows bucket count to keep load under `maxLoad` and rethreads all entries. Entry index `0` is reserved as null, so stable indices start at 1.

Dependencies and integration points: used internally by `Index` for each blob type. The stable first index is consumed by `AssociatedSet`. `maphash` protects against crafted low-bit SHA-256 collision attacks on hash table buckets.

Risks and test signals: no deletion support by design. Bit packing depends on word size and guards overflow by panic. Hash seed handling constructs a new `maphash.Hash` per call with the stored seed. Tests cover insertion/get, iteration, duplicate IDs, stable first indices, hashed array tree allocation, and hash benchmark.
