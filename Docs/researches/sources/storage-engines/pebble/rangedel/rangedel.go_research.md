# Research: sources/storage-engines/pebble/rangedel/rangedel.go

- **Purpose:** Public shim package exposing selected internal range-deletion span primitives to callers that need to decode or fragment range tombstones without importing internal packages.
- **Important APIs/types/functions:** Type aliases export `keyspan.Fragmenter`, `keyspan.Key`, and `keyspan.Span`. `Decode(ik sstable.InternalKey, val []byte, keysDst []Key) Span` delegates to `internal/rangedel.Decode` and appends to optional scratch storage to reduce allocations.
- **Control flow:** There is no internal branching beyond the wrapper call. Callers pass an encoded range-deletion internal key and value; the internal decoder returns a span representing the tombstone bounds and key metadata.
- **State and persistence behavior:** The package holds no state and writes nothing. It interprets persisted sstable/log encoded range-deletion records through `sstable.InternalKey` and value bytes supplied by callers.
- **Dependencies:** Depends on `internal/keyspan` for exported aliases, `internal/rangedel` for the real decoder, and `sstable` for public `InternalKey` typing.
- **Integration points:** Supports tools and package users that consume Pebble sstable range tombstones. It preserves a narrow public surface while allowing internals to keep the actual encoding logic centralized.
- **Risks:** Because it is an alias/delegation layer, risk is mainly API compatibility and semantic drift if internal `keyspan` or range-deletion encoding changes. Incorrect caller assumptions about key kind or encoded value are handled by the internal decoder rather than this file.
- **Test signals:** No local tests in this file. Coverage is indirect through sstable range-deletion encoding/decoding tests, compaction/replay paths that round-trip range tombstones, and any external package tests importing `rangedel.Decode`.
