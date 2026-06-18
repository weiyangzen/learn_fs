<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/tuple/tuple_test.go -->
# sources/storage-engines/foundationdb/bindings/go/src/fdb/tuple/tuple_test.go

Purpose: validates tuple packing stability and tuple string rendering.

Important tests: deterministic random generator setup; golden load/write helpers for `testdata/tuples.golden`; representative tuple cases covering UUIDs, strings/bytes with nulls, integers, floats, doubles, booleans, nils, nested tuples, and large byte arrays. `TestTuplePacking` compares `Tuple.Pack` output against golden bytes unless `-update` is set. `BenchmarkTuplePacking` measures packing. `TestTupleString` checks rendering of bytes, strings, nested tuples, booleans, UUIDs, and versionstamps.

Control flow/state: uses gob-encoded golden data and optional update mode that rewrites the golden file. Random input is made deterministic with a local `rand.Rand` seed for Go 1.20+ stability.

Dependencies and integration: depends on tuple encoder, stringer, `fdb.Printable`, and local testdata.

Risks: update mode can bless regressions if used casually. Golden tests validate packing but not unpack round trips or malformed decode errors in this file. Randomly generated cases are deterministic but limited.

Test signals: strong regression signal for binary compatibility of tuple keys, which is critical for persistence and cross-language compatibility.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/tuple/tuple_test.go -->
