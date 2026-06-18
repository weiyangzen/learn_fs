<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_commit2_latency.cc -->
## sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_commit2_latency.cc

Purpose: benchmark and smoke-test `commit2` and wrapper `fsal_commit` on an opened file.

Important APIs/types/functions: fixture allocates a share state, opens `TEST_FILE` with `open2`, and closes/removes it in teardown. Tests call `test_file->obj_ops->commit2`, `fsal_commit`, `fsal_write`, and `mdcdb_get_sub_handle`. Writes use `fsal_io_arg`, `fsal_io_direction`, offsets, lengths, and stable/unstable flags.

Control flow/state: `SIMPLE` and `SIMPLE_BYPASS` commit a fixed range. Four write tests perform small/large stable/unstable writes then commit the written range. `LOOP` times one million direct `commit2` calls, and `FSAL_COMMIT` times one million wrapper calls. Persistent file content lives in the export and is cleaned up in teardown.

Dependencies/integration: requires an FSAL supporting `open2`, `write`, and `commit2`; embedded Ganesha environment; optional CLI tracing/profiling values.

Risks: backends may treat stable writes or zero/no-op commits differently, so latency comparisons are backend-specific. One million commit calls can be expensive on durable storage. Stack allocation for I/O args must match buffer sizes.

Test signals: assertions verify write return and commit status; stderr reports average `commit2` and `fsal_commit` latency.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_commit2_latency.cc -->
