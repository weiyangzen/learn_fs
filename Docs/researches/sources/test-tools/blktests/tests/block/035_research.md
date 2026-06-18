<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/block/035 -->
# sources/test-tools/blktests/tests/block/035

Source read: complete file, 92 lines, 2137 bytes, sha256 `1a3d002773b9c517`.

Purpose: blktests `block/035` case, `shared tag set fairness`. It is a harness-executed destructive/block-layer regression or behavior test (TIMED=1). It creates two memory-backed null_blk devices sharing a tag set with very different completion latencies, runs io_uring fio against both, records IOPS in `TEST_RUN`, and fails if the fast queue underperforms the slow one.

Important APIs/types/functions: shell hooks `requires, test`; requirement/condition hooks `requires`; sourced libraries `tests/block/rc, common/null_blk`. It calls helpers/commands `_configure_null_blk, _exit_null_blk, _have_fio, _have_module, _have_module_param, _init_null_blk, _io_uring_enable, _io_uring_restore, fio, sed`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `shared tag set fairness` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `block`, common libraries, root privileges, udev, and kernel facilities exercised by `shared tag set fairness`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `block/035`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/block/035.out` exists with 2 lines; first signals: `Running block/035; Passed`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/block/035 -->
