# sources/sync-backup/kopia/repo/content/index/index_builder.go

Final split target: `Docs/researches/sources/sync-backup/kopia/repo/content/index/index_builder.go_research.md`.

Purpose: builds binary pack indexes from `Info` records, including deduplication by content ID, stable sorted ordering, random uniqueness suffixes, and sharding for large index blobs.

Important APIs: `Builder` is a `map[ID]Info`. `Clone` copies the map. `Add` replaces entries only when the new info wins by `contentInfoGreaterThanStruct`. `sortedContents` bucket-sorts by prefix and first hash nibble, sorting buckets in parallel. `Build`, `buildStable`, `buildSortedContents`, `shard`, and `BuildShards` serialize indexes in v1 or v2 format.

Control flow: `Build` writes stable content then appends a 32-byte random suffix so otherwise identical indexes have unique blob IDs. `BuildShards` distributes IDs by FNV hash of `ContentID.String()` to keep shards below a maximum item count, builds each stable shard, and optionally appends random suffixes.

State and persistence behavior: the builder is mutable in memory until serialized. Persisted index contents are sorted immutable records. Stable builds are used where deterministic output matters; non-stable builds ensure encrypted blob names do not collide.

Dependencies: `gather`, crypto randomness, FNV, runtime CPU count, sorting, maps, and v1/v2 builders.

Risks and tests: bucket sorting assumes valid ID bytes and must remain order-compatible. Shard distribution must cover every ID exactly once. Tests validate stable prefixes, random suffix differences, sorted order, sharding counts, and v1/v2 round trips.
