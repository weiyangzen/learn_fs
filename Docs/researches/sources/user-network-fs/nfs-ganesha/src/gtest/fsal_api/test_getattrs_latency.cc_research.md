<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_getattrs_latency.cc -->
## sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_getattrs_latency.cc

Purpose: benchmarks attribute retrieval through MDCACHE and backend-bypass paths.

Important APIs/types/functions: tests call `obj_ops->getattrs`, `get_optional_attrs`, `obj_ops->lookup`, `mdcdb_get_sub_handle`, `create_and_prime_many`, and `remove_many`. Constants use `DIR_COUNT = 100000` and `LOOP_COUNT = 1000000`.

Control flow/state: simple tests get attributes for the root and its sub-handle. `GET_OPTIONAL_ATTRS` loops over optional attribute collection. Full fixture primes many files. `BIG_CACHED` repeatedly reads the same root handle; `BIG_UNCACHED` looks up many file handles before timing getattrs; bypass variants repeat against sub-handles. References from lookup are released after timing.

Dependencies/integration: embedded Ganesha, MDCACHE debug helper for bypass, and a writable export capable of creating 100000 files.

Risks: arrays sized at one million handles/sub-handles are memory-heavy. `BIG_BYPASS_UNCACHED` stores backend handles after releasing MDCACHE wrapper objects; correctness depends on sub-handle lifetime rules. No `fsal_release_attrs` appears for output attrs, so future attr allocations would need scrutiny.

Test signals: zero major status on all attribute calls and printed average timings for optional, cached, uncached, and bypass getattrs paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_getattrs_latency.cc -->
