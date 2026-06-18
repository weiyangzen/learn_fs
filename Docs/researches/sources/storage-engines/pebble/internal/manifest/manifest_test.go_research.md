# sources/storage-engines/pebble/internal/manifest/manifest_test.go

## Purpose
This external-package integration test validates `Version.CalculateInuseKeyRanges` against a randomly generated Pebble database produced by metamorphic tests. It checks the manifest replay path and in-use range calculation on realistic database state.

## Important APIs And Helpers
- `TestInuseKeyRangesRandomized` runs a metamorphic workload, replays the generated manifest, chooses random spans and start levels, and verifies coverage.
- `replayManifest` uses `pebble.Peek`, `record.Reader`, `VersionEdit.Decode`, `BulkVersionEdit.Accumulate`, `BulkVersionEdit.Apply`, and `L0Organizer.PerformUpdate` to reconstruct the current manifest version.

## Control Flow
The test creates random Pebble operations, executes them, replays the manifest into a fresh `Version`, then performs 200 randomized range checks. For every overlapping file at or below the chosen level, it truncates the file bounds to the query span and asserts some returned in-use range contains that truncated span.

## State And Persistence Behavior
This file explicitly exercises persisted MANIFEST state. It does not rely on in-memory DB structures after the metamorphic run; it reopens manifest records and reconstructs the version state from encoded edits.

## Dependencies And Integration Points
It integrates the public `pebble` package with `internal/manifest`, `metamorphic`, `record`, `base`, `testkeys`, and build tags. Running in package `manifest_test` gives a useful external-consumer perspective.

## Risks And Test Signals
The test is randomized and may expose rare in-use range bugs that deterministic fixtures miss. It is heavier than normal unit tests and scales down operation count under slow/instrumented builds. Failures include the random seed for replay.
