# sources/test-tools/crashmonkey/code/results/SingleTestInfo.h

Purpose: declares the per-test result container that combines crash-state, data-test, and filesystem-test information.

Important APIs/types: `ResultType` includes passed, fsck fixed, fsck required, and failed. Public fields are `test_num`, `fs_test`, `data_test`, and `permute_data`.

Control flow and integration: `Tester` fills and prints this object for each tested crash state, then passes it to `TestSuiteResult` tally methods.

State: no persistence beyond logs. Public mutable fields keep construction lightweight.

Risks: the header comments warn about memory consumption for very large test counts. Public fields make invalid partial states easy to construct. `test_num` is not visibly initialized in the header.

Test signals: ensure every `ResultType` prints correctly and downstream suite tallies match classifications.
