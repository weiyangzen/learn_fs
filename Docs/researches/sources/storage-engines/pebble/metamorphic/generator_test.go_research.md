# sources/storage-engines/pebble/metamorphic/generator_test.go

## Purpose
`generator_test.go` validates the random operation generator's determinism and its object-lifetime bookkeeping. It also tests helper behavior for disjoint snapshot ranges and CockroachDB-style suffix keyspace materialization.

## Important Tests and Helpers
- `TestGenerator` manually exercises `newBatch`, `newIndexedBatch`, `newIter`, `batchAbort`, `newSnapshot`, `snapshotClose`, and `writerApply` to verify live sets and maps are drained correctly.
- `TestGeneratorRandom` generates 1k-10k operations from a fixed seed across default and multi-instance configs, then regenerates ten times and diffs formatted operations.
- `TestGenerateDisjointKeyRanges` repeatedly checks that generated ranges are ordered and non-overlapping.
- `TestCockroachSuffixKeyspace` checks `cockroachSuffixKeyspace` conversion between `suffixIndex` and formatted MVCC suffix strings for several maximum logical timestamp values.

## Control Flow and State
The tests build generators with `randvar.NewRand`, `DefaultOpConfig`, `multiInstanceConfig`, and `newKeyManager`. `TestGenerator` inspects internal generator fields such as `liveBatches`, `batches`, `readers`, `liveIters`, `iters`, `liveSnapshots`, `snapshots`, and `liveWriters`, ensuring close/remove paths erase secondary indexes as well as primary live lists.

`TestGeneratorRandom` intentionally reconstructs the RNG with `rand.NewPCG(0, seed)` for each generation and asserts formatted operation streams are byte-identical. That catches accidental use of global randomness inside generation paths.

## Dependencies and Integration Points
The file uses `cockroachkvs` formatting for suffix tests, `randvar` for deterministic random helpers, `difflib` for readable operation diffs, and `testify/require` assertions. It targets unexported generator internals within the same package, so it is tightly coupled to generator field names and lifecycle invariants.

## Risks and Edge Cases
- The deterministic generation test does not assert semantic quality of every generated operation, but it is strong at detecting hidden non-deterministic RNG sources.
- The lifecycle tests focus on representative close paths; new object kinds or live-object indexes should add analogous assertions.
- Disjoint key range testing samples generated ranges but does not prove all key formats and distributions.

## Test Signals
This is itself the test signal for `generator.go`. Failures here usually mean operation streams cannot be reproduced, object closure could race or leak, bounded snapshot ranges can overlap, or suffix-format assumptions changed.
