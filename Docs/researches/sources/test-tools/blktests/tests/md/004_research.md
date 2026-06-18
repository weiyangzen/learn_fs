<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/md/004 -->
# sources/test-tools/blktests/tests/md/004

Source read: complete file, 98 lines, 2676 bytes, sha256 `951febb747dde09b`.

Purpose: blktests `md/004` case, `test unmap write zeroes sysfs interface with MD devices`. It is a harness-executed destructive/block-layer regression or behavior test (QUICK=1).

Important APIs/types/functions: shell hooks `requires, setup_test_device, cleanup_test_device, test`; requirement/condition hooks `requires`; sourced libraries `tests/md/rc, common/scsi_debug`. It calls helpers/commands `_configure_scsi_debug, _exit_scsi_debug, _have_driver, _have_scsi_debug, _real_dev, mdadm, cat`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `test unmap write zeroes sysfs interface with MD devices` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `md`, common libraries, root privileges, udev, and kernel facilities exercised by `test unmap write zeroes sysfs interface with MD devices`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `md/004`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/md/004.out` exists with 2 lines; first signals: `Running md/004; Test complete`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/md/004 -->
