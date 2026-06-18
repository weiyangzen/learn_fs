<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/cppsuite_test_run.sh -->
# sources/storage-engines/wiredtiger/test/evergreen/cppsuite_test_run.sh

Purpose: wrapper for running a single cppsuite workload in Evergreen while temporarily adjusting Linux perf permissions needed by latency/performance collection.

Control flow: validates one to three arguments (`test_name`, `test_config_filename`, `test_config`), reads the current `kernel.perf_event_paranoid` value with `sudo sysctl`, sets it to `2`, runs `./run -t ... -C ... -f ... -l 2`, captures exit code, restores the original sysctl value, writes `cppsuite_exit_code`, and if the test failed writes a minimal empty-metrics JSON file named after the test.

State and persistence: mutates kernel sysctl during execution; writes `cppsuite_exit_code` and possibly `<test_name>.json`.

Dependencies and integration: called from Evergreen cppsuite test functions in `test/evergreen.yml`, from the cppsuite build directory where `./run` exists.

Risks and test signals: exits `0` even if the test fails, pushing failure signaling into `cppsuite_exit_code` and generated JSON. Requires passwordless or configured `sudo`. Restoring sysctl is not protected by a trap, so abrupt termination can leave the changed setting.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/cppsuite_test_run.sh -->
