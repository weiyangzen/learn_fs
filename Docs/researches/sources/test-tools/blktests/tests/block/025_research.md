<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/block/025 -->
# sources/test-tools/blktests/tests/block/025

Source read: complete file, 34 lines, 791 bytes, sha256 `b5191d3957a84eff`.

Purpose: blktests `block/025` case, `do a huge discard with 4k sector size`. It is a harness-executed destructive/block-layer regression or behavior test (no explicit quick/timed flag).

Important APIs/types/functions: shell hooks `requires, test`; requirement/condition hooks `requires`; sourced libraries `tests/block/rc, common/scsi_debug`. It calls helpers/commands `_exit_scsi_debug, _have_loadable_scsi_debug, _init_scsi_debug, blkdiscard`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `do a huge discard with 4k sector size` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `block`, common libraries, root privileges, udev, and kernel facilities exercised by `do a huge discard with 4k sector size`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `block/025`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/block/025.out` exists with 2 lines; first signals: `Running block/025; Test complete`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/block/025 -->
