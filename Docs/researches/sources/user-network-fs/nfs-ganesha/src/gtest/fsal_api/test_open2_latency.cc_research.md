<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_open2_latency.cc -->
## sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_open2_latency.cc

Purpose: benchmarks `open2` through wrapper, object op, bypass, and open-existing-only paths.

Important APIs/types/functions: fixtures prepare `fsal_attrlist attrs_in` and allocate arrays of `STATE_TYPE_SHARE` states. Tests call `fsal_open2`, `obj_ops->open2`, `obj_ops->close2`, `fsal_close`, `fsal_create`, `fsal_remove`, `nfs_export_get_root_entry`, and `mdcdb_get_sub_handle`.

Control flow/state: simple tests open/create one file with share state, close it, remove it, and release state/handle. Loop tests open 100000 generated files while timing wrapper or direct `open2`, then close/remove. `OPEN_ONLY` pre-creates files, then times opening existing files without create cost.

Dependencies/integration: requires open2-capable FSAL, state allocation/free support from export ops, MDCACHE bypass support, and a writable export.

Risks: loops allocate many states/files and can hit resource limits. Bypass tests combine backend handles with Ganesha state objects; correctness depends on compatible state ownership. `OPEN_ONLY` creates files under `root_entry` but later opens/removes via `test_root`, so path relationships must match fixture setup.

Test signals: zero status for create/open/close/remove, non-null backend handles, and average timings for `fsal_open2`, direct `open2`, bypass `open2`, and open-only paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_open2_latency.cc -->
