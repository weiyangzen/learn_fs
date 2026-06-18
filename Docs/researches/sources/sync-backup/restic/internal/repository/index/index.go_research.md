## sources/sync-backup/restic/internal/repository/index/index.go

Purpose: in-memory and serialized representation of restic index files mapping blob handles to pack locations.

Important APIs/types: `Index` holds per-type `indexMap`s, pack IDs, final/index IDs, creation time, and a mutex. `NewIndex`, `StorePack`, `Lookup`, `Has`, `LookupSize`, `Values`, `EachByPack`, `Packs`, `Encode`, `SaveIndex`, `Finalize`, `IDs`, `SetID`, `Dump`, `DecodeIndex`, `BlobIndex`, `Len`, and `PackBlobsHash` are the main API. `Full` and `Oversized` decide when index files should be saved/split. JSON structs `packJSON`, `blobJSON`, and `jsonIndex` define on-disk index shape.

Control flow and state: mutable indexes accept `StorePack` until finalized. Finalized indexes can be saved and assigned exactly one ID. `LookupSize` returns uncompressed length for compressed blobs or subtracts crypto overhead otherwise. `EachByPack` groups entries by pack and optionally ignores blacklisted packs only for finalized indexes. `merge` combines finalized indexes and removes exact duplicate packed blobs. `DecodeIndex` builds a finalized index from JSON and accepts older JSON with ignored `supersedes` fields.

Dependencies and integration points: central to repository load/save/check/prune/repair paths. It depends on `pack`, `crypto` length helpers, `restic` IDs/blob types, and the custom `indexMap` for memory efficiency.

Risks and test signals: panics guard impossible pack offsets over 4 GiB, storing into finalized indexes, null pack IDs, unsupported merge state, and ID assignment order. Iterator methods hold locks while yielding, so callbacks must not attempt mutation. Tests cover serialization, doc examples, size/counts, lookup/type separation, pack listing, grouping by pack, blacklist behavior, oversized thresholds, and benchmarks.
