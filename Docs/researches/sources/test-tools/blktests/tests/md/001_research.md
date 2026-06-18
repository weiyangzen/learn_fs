<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/md/001 -->
# sources/test-tools/blktests/tests/md/001

Source read: complete file, 88 lines, 1933 bytes, sha256 `cf7a8b0be439a52f`.

Purpose: blktests `md/001` case, `Raid with bitmap on tcp nvmet with opt-io-size over bitmap size`. It is a harness-executed destructive/block-layer regression or behavior test (QUICK=1).

Important APIs/types/functions: shell hooks `requires, setup_underlying_device, cleanup_underlying_device, setup_nvme_over_tcp, cleanup_nvme_over_tcp, test`; requirement/condition hooks `requires`; sourced libraries `tests/md/rc, common/brd, common/nvme`. It calls helpers/commands `_cleanup_brd, _create_nvmet_host, _create_nvmet_port, _create_nvmet_subsystem, _find_nvme_ns, _have_brd, _have_driver, _have_nvme_cli_with_json_support, _have_program, _init_brd, _nvme_connect_subsys, _nvme_disconnect_subsys, _nvmet_target_cleanup, _require_nvme_trtype, _setup_nvmet, blockdev, dmsetup, mdadm`.

Control flow: The blktests runner sources the file, evaluates `requires`/`device_requires`/`set_conditions` when present, then invokes `test`. The body prints `Running ${TEST_NAME}`, prepares temporary or configured block devices, performs the `Raid with bitmap on tcp nvmet with opt-io-size over bitmap size` scenario, records detailed command output in `$FULL` or `TEST_RUN` when needed, and relies on explicit teardown or registered cleanup from sourced libraries.

State and persistence behavior: The test may alter block-device sysfs attributes, kernel modules/configfs/debugfs, udev-visible devices, files in `$TMPDIR`, and output under `$RESULTS_DIR`. It is intended to leave no persistent state after cleanup, but must be run only with disposable `$TEST_DEV`/`TEST_DEV_ARRAY` devices because many cases write, discard, repartition, detach, or fault-inject devices.

Dependencies and integration points: Integrates with the blktests harness variables (`TEST_NAME`, `TEST_DEV`, `TEST_DEV_SYSFS`, `TMPDIR`, `FULL`, `RESULTS_DIR`, `SKIP_REASONS`, `TEST_RUN`), group rc file for `md`, common libraries, root privileges, udev, and kernel facilities exercised by `Raid with bitmap on tcp nvmet with opt-io-size over bitmap size`.

Risks: Races and timing-sensitive checks can be flaky on slow machines or busy CI. Missing cleanup after failure can leave null_blk/scsi_debug/loop/dm/md/bcache state active. Kernel feature probes must skip cleanly on unsupported versions; otherwise tests can fail for environment reasons rather than regressions.

Test signals: A successful run should match the harness pass/skip contract for `md/001`, include no unexpected dmesg failures after group filters, and compare cleanly against any expected output fixture. Expected output fixture `sources/test-tools/blktests/tests/md/001.out` exists with 3 lines; first signals: `Running md/001; disconnected 1 controller(s); Test complete`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/md/001 -->
