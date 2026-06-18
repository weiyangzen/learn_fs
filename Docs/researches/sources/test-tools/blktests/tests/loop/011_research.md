<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/loop/011 -->
# sources/test-tools/blktests/tests/loop/011

Source read: complete file, 41 lines, 1172 bytes, sha256 `93754ebf055b7f35`.

Purpose: blktests `loop/011` case, `Make sure unsupported backing file fallocate does not fill dmesg with errors`. It is a harness-executed destructive/block-layer regression or behavior test (no explicit quick/timed flag).

Important APIs/types/functions: shell hooks `requires, test`; requirement/condition hooks `requires`; sourced libraries `tests/loop/rc`. It calls helpers/commands `_dmesg_since_test_start, _have_kver, _have_program, dd, losetup, mkfs.ext2, mount, umount, grep`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `Make sure unsupported backing file fallocate does not fill dmesg with errors` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `loop`, common libraries, root privileges, udev, and kernel facilities exercised by `Make sure unsupported backing file fallocate does not fill dmesg with errors`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `loop/011`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/loop/011.out` exists with 3 lines; first signals: `Running loop/011; Found 1 error(s) in dmesg; Test complete`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/loop/011 -->
