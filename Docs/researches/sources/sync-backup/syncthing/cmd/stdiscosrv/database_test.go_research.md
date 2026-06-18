# sources/sync-backup/syncthing/cmd/stdiscosrv/database_test.go

Purpose: unit and benchmark coverage for discovery database records, expiry, and merge behavior.

Important APIs/tests: `TestDatabaseGetSet`, `TestFilter`, `TestMerge`, `BenchmarkMergeEqual`, and `testClock`.

Control flow and state: tests use temporary stores and a controllable clock to validate reads, lazy expiry, statistics-era pruning, and merge ordering. Merge cases cover nil inputs, duplicate addresses with newer expiry, disjoint ordered inputs, reverse merge symmetry, and preserving maximum expiry per address.

Dependencies/integration: depends on generated discovery protobuf address records and local database helpers.

Risks and test signals: tests document the sorted-address precondition and expected union semantics. Benchmark asserts the equal-address merge path remains allocation-free. Tests do not cover file serialization round trips with corrupt records, blob fallback, or concurrent `xsync` access.
