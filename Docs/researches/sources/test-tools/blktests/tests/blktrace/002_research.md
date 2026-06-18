<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/blktrace/002 -->
# sources/test-tools/blktests/tests/blktrace/002

Source read: complete file, 97 lines, 2452 bytes, sha256 `bcf1382e929319ef`.

Purpose: blktests `blktrace/002` case, `blktrace ftrace corruption with sysfs trace`. It is a harness-executed destructive/block-layer regression or behavior test (QUICK=1).

Important APIs/types/functions: shell hooks `requires, test`; requirement/condition hooks `requires`; sourced libraries `tests/blktrace/rc, common/null_blk`. It calls helpers/commands `_configure_null_blk, _exit_null_blk, _have_null_blk, _have_tracefs, dd, blktrace, grep`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `blktrace ftrace corruption with sysfs trace` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `blktrace`, common libraries, root privileges, udev, and kernel facilities exercised by `blktrace ftrace corruption with sysfs trace`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `blktrace/002`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/blktrace/002.out` exists with 3 lines; first signals: `Running blktrace/002; Trace output looks correct; Test complete`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/blktrace/002 -->
