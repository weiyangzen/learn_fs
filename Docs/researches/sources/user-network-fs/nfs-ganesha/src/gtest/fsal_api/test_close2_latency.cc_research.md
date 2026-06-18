<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_close2_latency.cc -->
## sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_close2_latency.cc

Purpose: latency/correctness benchmark for the FSAL `close2` object operation.

Important APIs/types/functions: fixtures derive from `gtest::GaneshaFSALBaseTest`. `Close2LoopLatencyTest` preallocates `STATE_TYPE_SHARE` states through `op_ctx->fsal_export->exp_ops.alloc_state` and frees them with `free_state`. Tests call `test_root->obj_ops->open2`, `obj->obj_ops->close2`, `mdcdb_get_sub_handle`, and `fsal_remove`.

Control flow/state: `SIMPLE` opens one file with a state, closes it with `close2`, removes it, drops the object ref, and frees state. `SIMPLE_BYPASS` closes the MDCACHE sub-handle. `LOOP` and `LOOP_BYPASS` create/open 100000 files, time only the close loop, then remove files and release refs.

Dependencies/integration: embeds Ganesha via the gtest environment, needs a configured export id, and can parse common CLI options for config/log/debug/export/LTTng/profile.

Risks: the source contains a malformed-looking chained `opts.add_options()` stanza around the `export` option that should be watched in builds. Loop count is large and consumes many states/files. Bypass mode relies on MDCACHE internals.

Test signals: assertions check zero major status and non-null state/sub-handles; timing output reports average nanoseconds per `close2`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_close2_latency.cc -->
