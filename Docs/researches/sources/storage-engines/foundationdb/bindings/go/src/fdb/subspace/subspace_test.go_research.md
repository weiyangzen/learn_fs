<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/subspace/subspace_test.go -->
# sources/storage-engines/foundationdb/bindings/go/src/fdb/subspace/subspace_test.go

Purpose: focused unit test for subspace string formatting.

Important test: `TestSubspaceString` constructs `Sub([]byte("hello"), "world", 42, 0x99)`, formats it with `fmt.Sprint`, and expects a `Subspace(rawPrefix=...)` string with FoundationDB tuple type codes rendered through `fdb.Printable`.

Control flow/state: no database access. It exercises tuple packing, subspace construction, `String`, and printable byte escaping.

Dependencies and integration: depends on `subspace.Sub`, tuple encoding, and `fdb.Printable`.

Risks: the test is narrow; it will catch formatting/encoding changes for one mixed tuple but not `Pack`, `Unpack`, range endpoints, versionstamps, or mutation-safety of returned bytes.

Test signals: good fast unit signal for developer-facing diagnostics; should be complemented by round-trip and range tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/subspace/subspace_test.go -->
