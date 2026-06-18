# Research: sources/storage-engines/pebble/rangekey/rangekey.go

- **Purpose:** Public shim package exposing selected range-key helpers and span primitives while delegating the actual encoding semantics to Pebble internals.
- **Important APIs/types/functions:** Type aliases export `keyspan.Fragmenter`, `keyspan.Key`, and `keyspan.Span`. `IsRangeKey(ik sstable.InternalKey) bool` checks whether an internal key kind is a range-key kind through `internal/rangekey.IsRangeKey`. `Decode(ik sstable.InternalKey, val []byte, keysDst []Key) (Span, error)` delegates to `internal/rangekey.Decode`.
- **Control flow:** The package is a thin pass-through. `Decode` validates and interprets the internal key/value via the internal package, returning errors for malformed or non-range-key records as defined there.
- **State and persistence behavior:** No mutable state. It decodes persisted range-key records from sstable or log material supplied by callers, with optional scratch reuse for span keys.
- **Dependencies:** Depends on `internal/keyspan`, `internal/rangekey`, and `sstable`. It deliberately avoids reimplementing range-key kind mappings or value parsing.
- **Integration points:** Used by public tooling and by replay code when reconstructing batches from raw sstable range-key spans. It provides a stable non-internal import path for consumers that need to inspect Pebble range keys.
- **Risks:** API risk is concentrated in the aliases: callers may depend on `keyspan` layout through public aliases. Decode correctness depends entirely on the internal package and on callers passing matching internal-key/value pairs.
- **Test signals:** No local test file. Indirect coverage comes from Pebble range-key tests, sstable writer/reader range-key tests, replay reconstruction, and iterator masking tests that depend on valid range-key decoding.
