<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/block/007 -->
# sources/test-tools/blktests/tests/block/007

Source read: complete file, 78 lines, 1559 bytes, sha256 `acaa3f960a33d6d2`.

Purpose: blktests `block/007` case, `test classic and hybrid IO polling`. It is a harness-executed destructive/block-layer regression or behavior test (TIMED=1).

Important APIs/types/functions: shell hooks `requires, device_requires, fallback_device, cleanup_fallback_device, run_fio_job, test_device`; requirement/condition hooks `requires, device_requires`; sourced libraries `tests/block/rc, common/iopoll, common/null_blk`. It calls helpers/commands `_configure_null_blk, _exit_null_blk, _fio_perf, _have_fio_with_poll, _require_test_dev_supports_io_poll_delay, _test_dev_is_rotational, _test_dev_queue_get, _test_dev_queue_set`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test_device`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `test classic and hybrid IO polling` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `block`, common libraries, root privileges, udev, and kernel facilities exercised by `test classic and hybrid IO polling`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `block/007`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/block/007.out` exists with 2 lines; first signals: `Running block/007; Test complete`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/block/007 -->
