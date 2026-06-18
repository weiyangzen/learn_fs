## sources/storage-engines/pebble/tool/db_test.go

Purpose: thin test entry point for DB command datadriven fixtures.

Important APIs/types/functions: `TestDB(t *testing.T)` calls `runTests(t, "testdata/db_*")`, delegating all command construction, memfs fixture cloning, custom comparer/merger setup, deterministic time, and output normalization to `data_test.go`.

Control flow: Go’s test runner invokes `TestDB`, which expands every `testdata/db_*` datadriven file. Each datadriven command becomes a Cobra invocation against a newly built `tool.New` command set with the shared harness configuration.

State and persistence: persistence behavior is entirely fixture-driven. The shared harness clones referenced DB directories into a memory filesystem and keeps clone mappings across commands inside a datadriven file so mutating DB commands can be observed by later commands.

Dependencies and integration: depends directly only on `testing` and `runTests`, but indirectly exercises `db.go`, `db_io_bench.go`, `db_analyze_*`, and other registered tool commands when fixtures invoke them.

Risks: because this file has no assertions of its own, fixture naming is the test scope. New DB fixture files matching `db_*` are automatically included; missing fixtures or overly broad globs can change coverage.

Test signals: serves as the package-level signal that DB command output remains stable for checks, scans, get/set, properties, manifest inspection, checkpoints, upgrades, space estimates, and related fixture scenarios.
