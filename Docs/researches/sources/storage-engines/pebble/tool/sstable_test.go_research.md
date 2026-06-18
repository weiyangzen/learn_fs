# Research: sources/storage-engines/pebble/tool/sstable_test.go

## Purpose
`tool/sstable_test.go` is the entry point for datadriven tests covering the `sstable` CLI commands. It keeps test logic centralized in shared harness code and selects only fixtures whose names match `testdata/sstable_*`.

## Important APIs, Types, And Functions
The file defines `TestSSTable(t *testing.T)`, which delegates to `runTests(t, "testdata/sstable_*")`. There are no local helper types or assertions; the behavior depends on the broader `tool` package datadriven test harness.

## Control Flow
The Go test runner invokes `TestSSTable`; `runTests` discovers matching testdata files, executes the configured command sequences, and compares command output to expected datadriven output. This file is intentionally thin so all CLI tools share one execution and golden-output path.

## State And Persistence
No persistent state is mutated directly here. The datadriven harness may open fixture SSTables and databases under `tool/testdata`, but this file only declares the suite boundary.

## Dependencies And Integration Points
It depends on the package-local `runTests` helper and the `testing` package. Its integration point is the naming convention for datadriven fixture files, so adding a new `testdata/sstable_*` file automatically expands this suite.

## Risks And Edge Cases
Because this file delegates all work, failures may be difficult to localize from this file alone. The suite's completeness depends entirely on fixture coverage and on `runTests` setting up commands with the same flags and registered comparers used by production tooling.

## Test Signals
The signal is broad CLI regression coverage: command parsing, stdout/stderr rendering, fixture compatibility, formatter output, and golden diffs. A missing or incorrectly named fixture would silently fall outside this test.
