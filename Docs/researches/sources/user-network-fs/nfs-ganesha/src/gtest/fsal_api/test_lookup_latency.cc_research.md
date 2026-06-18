<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_lookup_latency.cc -->
## sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_lookup_latency.cc

Purpose: benchmarks lookup through MDCACHE, FSAL wrapper, and backend-bypass paths.

Important APIs/types/functions: tests call `root_entry->obj_ops->lookup`, `fsal_lookup`, `test_root->obj_ops->lookup`, `mdcdb_get_sub_handle`, `create_and_prime_many`, `remove_many`, `enableEvents`, `disableEvents`, and optional gperftools profiling. `FILE_COUNT = 100000`; `LOOP_COUNT = 1000000`.

Control flow/state: simple tests verify lookup of the test root from the export root and backend root. Loop tests repeatedly lookup the same root or wrapper API. Full tests prime a large directory and time single or many lookup calls across generated filenames. All returned handles are released.

Dependencies/integration: embedded Ganesha, MDCACHE debug support for bypass, optional LTTng and profiler integration, and a writable export.

Risks: benchmark timing can be dominated by cache state established during fixture priming. Large loop count and profiling can perturb results. Bypass tests compare backend handles to MDCACHE sub-handles, so pointer identity assumptions are backend/MDCACHE specific.

Test signals: zero status, expected handle identity, balanced `put_ref`, event/profiler bracketing, and average lookup timings for wrapper/direct/bypass/large-directory cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_lookup_latency.cc -->
