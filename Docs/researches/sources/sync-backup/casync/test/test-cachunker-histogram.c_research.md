# sources/sync-backup/casync/test/test-cachunker-histogram.c

Purpose: stress/diagnostic test for content-defined chunk size distribution.

Important APIs/types/functions: worker `process` threads feed random data through `CaChunker`, `draw` prints histogram bars, `run` computes average chunk size for a pick value, and `main` scans parameters.

Control flow/state: opens `/dev/urandom`, spawns threads, each records chunk-size counts in a histogram, then joins and aggregates. Assertions enforce min/max chunk bounds.

Dependencies/integration: depends on pthreads, chunker internals, random input, and terminal output for diagnostics.

Risks/test signals: statistical tests can be noisy and environment-dependent. The hard assertions check bounds; histogram/average output helps tune chunker parameters.

Source research group: `subset-b-009122`.
