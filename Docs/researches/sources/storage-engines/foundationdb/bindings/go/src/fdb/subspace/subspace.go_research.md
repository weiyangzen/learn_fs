<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/subspace/subspace.go -->
# sources/storage-engines/foundationdb/bindings/go/src/fdb/subspace/subspace.go

Purpose: implements the Go subspace layer, a tuple-prefixed key namespace abstraction.

Important APIs: `Subspace` interface, `AllKeys`, `Sub`, `FromBytes`, methods `Sub`, `Bytes`, `Pack`, `PackWithVersionstamp`, `Unpack`, `Contains`, `FDBKey`, `FDBRangeKeys`, `FDBRangeKeySelectors`, and helper `concat`.

Control flow: constructors create raw prefixes from tuple encodings or bytes. `Pack` appends tuple packing to the raw prefix. `Unpack` checks prefix membership then tuple-unpacks the suffix. Range methods return `[prefix+0x00, prefix+0xff)` selectors, representing tuple keys strictly inside the subspace.

State and persistence: subspaces are client-side byte prefixes. They do not persist metadata; they shape keys used by transactions.

Dependencies and integration: depends on `fdb` key/range interfaces and `tuple`. Used by directory layer, tests, and application code.

Risks: `Bytes` returns the internal slice directly, unlike `FromBytes` which clones input; external mutation of returned bytes can corrupt the subspace value. `Contains` only checks raw prefix, not tuple well-formedness. `AllKeys().FDBRangeKeys()` returns `[0x00,0xff)`, excluding keys outside tuple-style range endpoints.

Test signals: `subspace_test.go` verifies `String` formatting for a representative tuple prefix.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/subspace/subspace.go -->
