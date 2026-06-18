<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/block/036 -->
# sources/test-tools/blktests/tests/block/036

Source read: complete file, 87 lines, 2017 bytes, sha256 `40b65ab2f6cdcf7f`.

Purpose: blktests `block/036` case, `test return EIO from BLKRRPART for whole-dev`. It is a harness-executed destructive/block-layer regression or behavior test (QUICK=1). It saves global debugfs `fail_make_request` settings and per-device `make-it-fail`, forces I/O failure, runs `blockdev --rereadpt`, and expects an Input/output error before restoring all fault-injection settings.

Important APIs/types/functions: shell hooks `_have_debugfs, requires, test_device`; requirement/condition hooks `requires`; sourced libraries `tests/block/rc`. It calls helpers/commands `_have_debugfs, blockdev, grep, cat`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test_device`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `test return EIO from BLKRRPART for whole-dev` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `block`, common libraries, root privileges, udev, and kernel facilities exercised by `test return EIO from BLKRRPART for whole-dev`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `block/036`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/block/036.out` exists with 3 lines; first signals: `Running block/036; Return EIO for BLKRRPART on bad disk; Test complete`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/block/036 -->
