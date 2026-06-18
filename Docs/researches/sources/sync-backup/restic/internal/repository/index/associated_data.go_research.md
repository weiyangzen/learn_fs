## sources/sync-backup/restic/internal/repository/index/associated_data.go

Purpose: memory-efficient blob-handle set/map that stores small associated values using stable offsets from a `MasterIndex`.

Important APIs/types: `associatedSetSub[T]` stores parallel `value` and `isSet` slices. `AssociatedSet[T]` stores per-blob-type arrays, overflow map, and a master index. `NewAssociatedSet` sizes arrays from `mi.stableLen` for stable finalized index entries. `Get`, `Has`, `Set`, `Insert`, and `Delete` provide map/set operations. `Intersect` and `Sub` create derived sets while preserving values from the receiver. `Len`, `All`, `Keys`, and `String` provide iteration and display.

Control flow and state: handles found in the stable part of `MasterIndex` are addressed by `blobIndex`; missing or later-added handles fall back to `overflow`. `All` yields overflow entries first and then scans `mi.Values`, skipping duplicates already in overflow.

Dependencies and integration points: designed for high-volume repository operations such as prune/check where a normal Go map of blob handles would be memory-heavy. It depends on `MasterIndex` invariants that entries in the first merged finalized index have stable positions.

Risks and test signals: if `MasterIndex` is mutated substantially after creating a set, newly indexed blobs can land in overflow and memory benefits decrease. It is not synchronized. Tests cover normal entries, overflow entries, updates/deletes, sets created before index extension, intersection/subtraction, and string formatting.
