## sources/test-tools/syzkaller/prog/mutation_test.go

Purpose: validates that mutation can reach expected program transformations while preserving program validity and source-program immutability.

Important APIs/types/functions: `TestMutationFlags`, `TestChooseCall`, `TestMutateArgument`, `TestMutateNoSquash`, `TestSizeMutateArg`, `TestClone`, `TestMutateRandom`, `TestMutateCorpus`, `TestMutateTable`, `TestNegativeMutations`, `runMutationTests`, `buildTestContext`, and benchmarks for mutation/generation and integer store/load.

Control flow: table tests deserialize an original program and a goal program, build a choice table from the union of involved syscalls, mutate cloned originals with a deterministic random source, and compare serialized output. Random tests generate programs, mutate clones, deserialize mutated output, and ensure the original serialization is unchanged.

State and persistence: no persistent state. It exercises in-memory `Prog` clone, mutation, serialization, and deserialization state. The test helpers use deterministic `rand.Source` values to make probability-heavy mutation paths reproducible enough for goal-seeking loops.

Dependencies/integration: integrates with test target descriptions, `testutil.IterCount`, choice tables, serialization/deserialization, clone, and length assignment.

Risks: many tests are probabilistic and use high iteration counts, so they can be slow and are skipped under race mode in selected cases. Goal tests assert reachability, not exact distribution quality. Negative mutation tests guard against out-of-range ranged-buffer sizes.

Test signals: this file itself is the principal signal for mutation. It covers both focused table goals and randomized full-target mutation, plus benchmark coverage for hot paths.
