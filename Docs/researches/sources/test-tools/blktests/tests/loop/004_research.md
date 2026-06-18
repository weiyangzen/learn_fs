<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/loop/004 -->
# sources/test-tools/blktests/tests/loop/004

Source read: complete file, 46 lines, 951 bytes, sha256 `7dc1e1c8722052cf`.

Purpose: blktests `loop/004` case, `combine loop direct I/O mode and a custom block size`. It is a harness-executed destructive/block-layer regression or behavior test (QUICK=1).

Important APIs/types/functions: shell hooks `requires, test`; requirement/condition hooks `requires`; sourced libraries `tests/loop/rc, common/scsi_debug`. It calls helpers/commands `_exit_scsi_debug, _have_loadable_scsi_debug, _have_loop_set_block_size, _have_program, _have_src_program, _init_scsi_debug, dd, xfs_io, losetup, udevadm, cat`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `combine loop direct I/O mode and a custom block size` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `loop`, common libraries, root privileges, udev, and kernel facilities exercised by `combine loop direct I/O mode and a custom block size`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `loop/004`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/loop/004.out` exists with 4 lines; first signals: `Running loop/004; 1; 769bd186841c10e5b1106b55986206c0e87fc05a7f565fdee01b5abcaff6ae78  -`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/loop/004 -->
