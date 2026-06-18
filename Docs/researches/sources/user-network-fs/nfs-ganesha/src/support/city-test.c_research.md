<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/support/city-test.c -->
# sources/user-network-fs/nfs-ganesha/src/support/city-test.c

## Purpose
This is a known-answer test program for the vendored C implementation of CityHash. It validates CityHash64, seeded CityHash64, CityHash128, seeded CityHash128, and optionally SSE4.2 CRC variants against a large static table.

## Important APIs, Types, and Functions
Important constants are `kSeed0`, `kSeed1`, `kSeed128`, `kDataSize=1<<20`, `kTestSize=300`, the global `data` buffer, and `testdata[300][15]`. `setup` fills the data buffer with deterministic pseudo-random bytes. `Check` compares expected and actual `uint64` values and increments global `errors`. `Test` runs the hash functions for one offset/length pair. `main` initializes data, runs 299 small tests with offset `i*i` and length `i`, then runs one full-buffer test.

## Control Flow
The test constructs deterministic input, iterates through the expected table, and compares low/high halves of 128-bit outputs. Under `__SSE4_2__`, `Test` also validates `CityHashCrc128`, `CityHashCrc128WithSeed`, and all four words of `CityHashCrc256`.

## State and Persistence Behavior
State is process-local: a 1 MiB static input buffer and an integer error counter. The test writes failures to stderr and returns nonzero if any mismatch occurs.

## Dependencies and Integration Points
It depends on `city.h` and optionally `citycrc.h` when SSE4.2 is enabled. It is a direct regression test for `support/city.c` and compiler/endian behavior in the hash implementation.

## Risks and Test Signals
Risks include the large static expected table being hard to audit, `%llx` format assumptions for `uint64`, and coverage focusing on deterministic vectors rather than collision or distribution quality. Test signals are a zero exit status on little- and big-endian targets, with and without `__SSE4_2__`, and failure output identifying expected versus actual hash words.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/support/city-test.c -->
