<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/md/003 -->
# sources/test-tools/blktests/tests/md/003

Source read: complete file, 36 lines, 712 bytes, sha256 `b20cb1fa7fb3c1e8`.

Purpose: blktests `md/003` case, `test md atomic writes for NVMe drives`. It is a harness-executed destructive/block-layer regression or behavior test (QUICK=1).

Important APIs/types/functions: shell hooks `requires, device_requires, test_device_array`; requirement/condition hooks `requires, device_requires`; sourced libraries `tests/md/rc, common/nvme, common/xfs`. It calls helpers/commands `_md_atomics_test, _nvme_requires, _require_test_dev_is_nvme, _require_test_dev_size`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test_device_array`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `test md atomic writes for NVMe drives` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `md`, common libraries, root privileges, udev, and kernel facilities exercised by `test md atomic writes for NVMe drives`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `md/003`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/md/003.out` exists with 197 lines; first signals: `Running md_atomics_test; TEST 1 raid0 step 1 - Verify md sysfs atomic attributes matches - pass; TEST 2 raid0 step 1 - Verify sysfs atomic attributes - pass`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/md/003 -->
