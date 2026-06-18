# sources/storage-engines/pebble/sstable/compressionanalyzer/buckets_test.go

## Purpose
Datadriven tests for compression analyzer bucket classification and report formatting.

## Important APIs, Types, and Functions
- `TestBuckets` supports `block-size`, `compressibility`, `example-buckets-string`, and `example-buckets-csv` commands.
- `exampleBuckets` creates deterministic random aggregates across block kinds, sizes, compressibility categories, and profiles.

## Control Flow
Commands parse line-oriented numeric input for classifications or build a sample `Buckets` structure and format it with a configurable minimum sample threshold.

## State and Persistence Behavior
The example bucket generator uses a fixed PCG seed, making report output stable. It populates Welford accumulators rather than hard-coding formatted rows.

## Dependencies and Integration Points
Uses `datadriven`, `crstrings`, `blockkind.All`, `rand/v2`, and the production formatting APIs.

## Risks and Edge Cases
Tests are golden-output sensitive; legitimate formatting changes require testdata updates. Randomized example generation is deterministic but still indirect, making individual bucket values less obvious from reading the test.

## Test Signals
Provides stable coverage for bucket boundaries and public report formats.
