<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/block/009 -->
# sources/test-tools/blktests/tests/block/009

Source read: complete file, 44 lines, 1125 bytes, sha256 `f8e6cfcbd8c189c0`.

Purpose: blktests `block/009` case, `check page-cache coherency after BLKDISCARD`. It is a harness-executed destructive/block-layer regression or behavior test (no explicit quick/timed flag).

Important APIs/types/functions: shell hooks `requires, test`; requirement/condition hooks `requires`; sourced libraries `tests/block/rc, common/scsi_debug`. It calls helpers/commands `_exit_scsi_debug, _have_loadable_scsi_debug, _have_program, _init_scsi_debug, dd, blkdiscard, xfs_io`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `check page-cache coherency after BLKDISCARD` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `block`, common libraries, root privileges, udev, and kernel facilities exercised by `check page-cache coherency after BLKDISCARD`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `block/009`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/block/009.out` exists with 8 lines; first signals: `Running block/009; 0000000 0000 0000 0000 0000 0000 0000 0000 0000; *`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/block/009 -->
