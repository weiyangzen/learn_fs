<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/run_model_workloads.sh -->
# sources/storage-engines/wiredtiger/test/evergreen/run_model_workloads.sh

Purpose: runs all model workload files through the model test tool in replay mode.

Control flow: changes to `cmake_build/test/model/tools`, validates `model_test`, iterates sorted `*.workload` files under `test/model/workloads`, skips workload `WT-12539` due to a tracked prepare-conflict issue, and runs `./model_test -R -h WT_TEST_<basename> -w <workload>`. It counts successes and failures, prints a summary, and exits nonzero if any workload failed.

State and persistence: creates per-workload `WT_TEST_*` homes in the model tools directory. It does not clean them.

Dependencies and integration: Evergreen memory/model workload tasks. Requires built `model_test`, workload files, and repo layout relative to build dir.

Risks and test signals: uses `[ $RESULT == 0 ]`, relying on Bash. Any nonzero model_test result increments failure but does not stop the loop, providing full workload coverage. The hard-coded skip should be revisited when WT-13232 is resolved.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/run_model_workloads.sh -->
