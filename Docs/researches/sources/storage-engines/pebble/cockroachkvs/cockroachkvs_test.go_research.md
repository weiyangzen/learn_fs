<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/cockroachkvs/cockroachkvs_test.go -->
# sources/storage-engines/pebble/cockroachkvs/cockroachkvs_test.go

## Purpose
Primary correctness tests for Cockroach key comparison, formatting/parsing, key writer/seeker logic, random key generation, and columnar data block encoding/iteration.

## Important APIs, Types, and Functions
`testPrefixes` and `testSuffixes` generate comparison cases including MVCC, synthetic, zero-logical, empty, and lock-table suffixes. `TestComparer` calls `base.CheckComparer`. `TestComparerFuncs`, `TestKeySchema_KeyWriter`, and `TestKeySchema_KeySeeker` are datadriven. `TestKeySeekerIsLowerBound`, `TestRandKeys`, `TestCockroachDataColBlock`, `testCockroachDataColBlock`, `generateDataBlock`, `randomQueryKeys`, formatting helpers, parsing helpers, and `TestFormatKey` cover randomized and round-trip behavior.

## Control Flow
Comparer tests generate prefixes/suffixes and verify ordering contracts. Datadriven writer tests parse user keys, compare against previous keys, write schema columns, materialize keys back, and print decoded columns. Seeker tests define blocks, initialize key seeker metadata, call `IsLowerBound`, `SeekGE`, and materialization with optional synthetic suffixes. Randomized block tests generate 100 key configurations, encode blocks, scan with `Next`, seek random keys, and ensure values match.

## State and Persistence Behavior
The tests operate on in-memory encoded blocks and no persistent files. They model persisted columnar block bytes and decode them into iterators/seeker metadata. Random key generation carries base wall time and distribution parameters.

## Dependencies and Integration Points
Depends on Pebble internal base keys, datadriven, `colblk`, block iterators, tablewriter output, Cockroach key helpers, `RandomKVs`, and generated testdata. It exercises the public comparer/key schema as a consumer would through block encoders and iterators.

## Risks and Edge Cases
Several randomized tests use time-based seeds and stop after a fixed number of generated configurations. Parser helpers panic on invalid inputs and are test-only. Datadriven expected output can be sensitive to formatting. The tests focus on point-key columnar behavior, with block property behavior covered only indirectly.

## Test Signals
Strong signals include comparer contract success, separator/successor output, exact writer/seeker datadriven transcripts, lower-bound equivalence to comparer ordering for single-row blocks, random scan and seek equality, value round trips, and format/parse round trips including panic checks for invalid formats.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/cockroachkvs/cockroachkvs_test.go -->
