<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/format_test_predictable.sh -->
# sources/storage-engines/wiredtiger/test/evergreen/format_test_predictable.sh

Purpose: validates deterministic replay of `test/format` by comparing multiple runs stopped at the same operation count/timestamp.

Control flow: accepts `times` and optional extra format args. For each iteration it runs `./t` with `CONFIG.replay` for a short timer into `RUNDIR_1`, reads the stable timestamp using `tools/wt_timestamps`, converts it to operations, then reruns from `RUNDIR_1/CONFIG` with `runs.timer=0` and `runs.ops=$ops` into `RUNDIR_2` and `RUNDIR_3` using different `random.extra_seed` values. It compares `RUNDIR_1` versus `RUNDIR_2`, then `RUNDIR_2` versus `RUNDIR_3`.

State and persistence: removes/recreates `RUNDIR_1/2/3`. On failure the `fail()` helper prints available CONFIG files and exits.

Dependencies and integration: called by Evergreen predictable format tasks from `cmake_build/test/format`. Depends on `./t`, `CONFIG.replay`, `tools/wt_timestamps`, and `tools/wt_cmp_dir`.

Risks and test signals: operation count comes from stable timestamp semantics; if timestamp extraction fails, arithmetic fails. Extra args are passed unquoted as a single variable. Directory compare failures are the main signal for nondeterminism.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/format_test_predictable.sh -->
