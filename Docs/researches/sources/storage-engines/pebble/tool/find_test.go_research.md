## sources/storage-engines/pebble/tool/find_test.go

Purpose: thin test entry point for the `find` command’s datadriven fixture.

Important APIs/types/functions: `TestFind` calls `runTests(t, "testdata/find")`.

Control flow: the shared harness builds the full tool command tree, clones referenced fixture DBs into memfs, and executes datadriven commands from `testdata/find`. Those commands exercise `find.go` through Cobra rather than direct helper calls.

State and persistence: fixture DBs are copied into an in-memory filesystem. Since `find` is read-only, persistence mainly concerns preserving the fixture layout of WALs, archived logs, SSTables, manifests, blob files, and catalogs.

Dependencies and integration: indirectly depends on `make_test_find_db.go` and `make_test_find_db_val_sep.go` generated fixtures, custom comparers/mergers from `data_test.go`, and blob/value formatting paths.

Risks: this file itself does not define coverage; all assertions live in the datadriven file. If generated fixture DBs drift without fixture updates, output expectations may fail.

Test signals: validates user-facing grouped output, key/value formatting, provenance strings, range tombstone discovery, WAL/SSTable ordering, and optional value-separation behavior covered by the fixture.
