<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/tuple/tuple.go -->
# sources/storage-engines/foundationdb/bindings/go/src/fdb/tuple/tuple.go

Purpose: implements FoundationDB tuple encoding/decoding for Go values with lexicographic order preservation.

Important APIs/types: `TupleElement`, `Tuple`, `UUID`, `Versionstamp`, `IncompleteVersionstamp`, `Versionstamp.Bytes`, `Tuple.Pack`, `Tuple.PackWithVersionstamp`, `HasIncompleteVersionstamp`, `Unpack`, `FDBKey`, `FDBRangeKeys`, `FDBRangeKeySelectors`, and string renderers.

Control flow: `packer.encodeTuple` dispatches by Go type, writes type codes, escapes embedded nulls in byte/string values, encodes signed/unsigned/big integers in order-preserving form, adjusts float sign bits, encodes nested tuples and versionstamps, and records the single incomplete versionstamp offset. `PackWithVersionstamp` requires selected API version, exactly one incomplete versionstamp, and appends 2- or 4-byte little-endian offset depending on API version. Decoding mirrors type codes with size/error checks.

State and persistence: no database writes. Encoded bytes become durable keys or values when used by transactions/subspaces. Versionstamp placeholders are completed by FDB commit mutations.

Dependencies and integration: uses `fdb.KeyConvertible`, `fdb.GetAPIVersion`, and `fdb.Printable`; consumed by subspace and directory layers.

Risks: panics on unsupported types and invalid vanilla incomplete versionstamps. Some decode paths index ahead and rely on well-formed lengths; malformed short integer encodings need scrutiny. `findTerminator` assumes a terminator exists and can misbehave on malformed input. API-version-dependent versionstamp offsets are subtle.

Test signals: `tuple_test.go` provides golden packing, benchmark, and string-format coverage.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/tuple/tuple.go -->
