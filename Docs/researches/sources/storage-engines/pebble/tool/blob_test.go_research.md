# sources/storage-engines/pebble/tool/blob_test.go

## Purpose
This file registers datadriven tests for the Pebble blob debug tool. It is intentionally small: its role is to connect the generic tool test runner to all blob-related fixture files.

## Important APIs, Types, and Functions
The only test is `TestBlob(t *testing.T)`, which calls `runTests(t, "testdata/blob_*")`. The implementation of `runTests` lives elsewhere in the `tool` package and provides command execution, fixture parsing, and output comparison.

## Control Flow
When the Go test runner executes `TestBlob`, the shared datadriven harness expands the glob `testdata/blob_*` and runs each matching fixture. Those fixtures are expected to invoke the `blob` command tree, including commands from `blob.go`, and compare stdout/stderr against golden output.

## State and Persistence Behavior
This file does not create state directly. Any persistent or in-memory state comes from the datadriven fixtures and shared harness. Because blob tooling reads real blob files and possibly manifests, the fixtures can validate layout rendering and blob-file mapping behavior without additional test code here.

## Dependencies and Integration Points
It depends on Go's `testing` package and the local `runTests` helper. It integrates with `newBlob`, `blobT.runLayout`, `blobFileMappings`, and other tool package command registration through the shared test harness.

## Risks and Edge Cases
The broad glob keeps the test file low maintenance but can hide which blob behaviors are covered unless the fixture names and contents are inspected. If no files match the glob, coverage depends on how `runTests` reports that condition. The test's precision is entirely determined by datadriven fixture quality.

## Test Signals
Passing `TestBlob` means all `testdata/blob_*` fixtures produce expected command output. Failures should be investigated in the fixture diff first, then in command wiring, blob layout decoding, or manifest-derived blob mapping.
