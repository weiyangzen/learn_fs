# sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_readdir_latency.cc

## Purpose
This executable benchmarks empty and populated directory enumeration through both direct object operations and the higher-level `fsal_readdir` helper. It includes normal MDCACHE-backed tests and sub-handle bypass tests.

## Important APIs, Types, And Functions
`ReaddirEmptyLatencyTest` creates one empty directory; `ReaddirFullLatencyTest` extends it by calling `create_and_prime_many(DIR_COUNT, NULL, test_dir)`. `populate_dirent` is the object-operation callback and releases each returned object. `FSALREADDIR` uses the `fsal_readdir` wrapper with the base fixture's static `readdir_callback`.

## Control Flow, State, And Persistence
Empty tests run one million iterations for direct and wrapper calls. Full tests create 100,000 entries and run 1,000 full directory scans. Timing encloses only the measured `readdir` calls; setup and cleanup populate and remove objects outside the measured window. `whence` is initialized to zero and reused, so the exact repeated-scan semantics depend on the FSAL's cookie handling and end-of-directory behavior.

## Dependencies And Integration Points
The file relies on `gtest.hh` for export setup and bulk create/remove helpers, MDCACHE debug helpers for `mdcdb_get_sub_handle`, FSAL object callback contracts, and Boost program option parsing. The test root name is `readdir_latency`.

## Risks And Test Signals
The loop count and directory size make the test an expensive microbenchmark. Reusing `whence` and `eod` across loop iterations may measure cached end-of-directory behavior rather than a cold full scan unless the FSAL resets or ignores those values as expected. Test signals are mostly status assertions and timing output; it does not verify returned entry identity, which is covered by the separate correctness test.
