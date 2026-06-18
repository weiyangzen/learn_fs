<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_link_latency.cc -->
## sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_link_latency.cc

Purpose: benchmarks hard-link creation via object ops and `fsal_link`.

Important APIs/types/functions: fixture creates `TEST_FILE` as source. Full fixture creates `DIR_COUNT = 100000` additional files. Tests call `test_file->obj_ops->link`, `fsal_link`, `lookup`, `fsal_remove`, `mdcdb_get_sub_handle`, `enableEvents`, `disableEvents`, and optional `ProfilerStart/Stop`.

Control flow/state: `SIMPLE` links the source, verifies both source and link by lookup, removes the link, and brackets with LTTng events. `SIMPLE_BYPASS` repeats against backend handles. Loop and full tests create many links, time creation, then remove links. Full variants measure behavior in a large directory.

Dependencies/integration: requires backend hard-link support, MDCACHE, LTTng/gperftools optional hooks, and a writable export.

Risks: hard links are unsupported or restricted on some FSALs/object backends. Large loops create one million names and can exhaust directory capacity or runtime. Bypass cleanup uses backend handles and may diverge from MDCACHE state if errors occur.

Test signals: zero status for link/remove, lookup identity checks in simple tests, and average timings for object-op, wrapper, large-directory, and bypass paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_link_latency.cc -->
