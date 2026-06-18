<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/loop/010 -->
# sources/test-tools/blktests/tests/loop/010

Source read: complete file, 94 lines, 2012 bytes, sha256 `accbfbc6a0c094b1`.

Purpose: blktests `loop/010` case, `check stale loop partition`. It is a harness-executed destructive/block-layer regression or behavior test (TIMED=1).

Important APIs/types/functions: shell hooks `requires, create_loop, detach_loop, test`; requirement/condition hooks `requires`; sourced libraries `tests/loop/rc`. It calls helpers/commands `_dmesg_since_test_start, _have_kver, _have_program, losetup, parted, mkfs.xfs, udevadm, blkid, grep`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `check stale loop partition` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `loop`, common libraries, root privileges, udev, and kernel facilities exercised by `check stale loop partition`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `loop/010`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/loop/010.out` exists with 2 lines; first signals: `Running loop/010; Test complete`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/loop/010 -->
