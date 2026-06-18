# sources/test-tools/crashmonkey/test/permuter/RandomPermuterTest.cpp

Purpose: lightweight gtests for `RandomPermuter`. It checks construction and basic behavior when generating one random crash state from single- and multi-epoch synthetic write streams.

Important APIs/types/functions: `RandomPermuter`, `disk_write`, `init_data`, `gen_one_state`, Linux block flags `REQ_WRITE`, `REQ_SYNC`, `REQ_FUA`, and gtest assertions.

Control flow: tests create vectors of writes and barriers, initialize the random permuter, request one state, and assert coarse properties. `FindOverlaps` expects output to differ when an overlapping barrier/write exists; `FindNoOverlapsMultiEpoch` expects the first non-overlapping epoch to be preserved.

State/persistence behavior: in-memory only; it tests permutation selection logic rather than actual replay. Dependencies/integration: depends on kernel block headers and `RandomPermuter` implementation.

Risks/test signals: because output is random, assertions are intentionally weak; no seed is controlled here, so reproducibility depends on implementation defaults. Still, it catches gross failures in overlap-aware randomization.
