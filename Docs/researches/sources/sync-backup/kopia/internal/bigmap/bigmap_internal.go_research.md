## sources/sync-backup/kopia/internal/bigmap/bigmap_internal.go

Purpose: implements a memory-efficient append-only hash table for binary keys and optional values, with dense segment storage and mmap spillover.

Important APIs/types/functions: `Options`, `internalMap`, `entry`, `Contains`, `Get`, `PutIfAbsent`, `Close`, `newInternalMapWithOptions`, `growLocked`, `findSlot`, `newSegment`, and mmap helpers.

Control flow, state, and persistence: keys must be 4..255 bytes and are stored as `[keyLen][key][varint valueLen][value]` in append-only segments. Slots store segment/offset pointers and use double hashing with prime table sizes; growth rebuilds slots from segment contents. A fixed number of memory segments is kept before creating auto-delete mmap files. `Close` runs cleanup functions in reverse. State is in-memory/tempfile-backed and not durable.

Dependencies and integration points: backing implementation for `bigmap.Map` and `bigmap.Set`, uses `mmap-go`, temp files, and repository logging.

Risks and test signals: risks include panic-driven invalid input handling, table-size index overflow at extreme scale, mmap creation fallback reducing memory guarantees, and no deletion/iteration. Tests and benchmarks cover growth, mmap spillover with tiny options, panics, and map/set behavior.
