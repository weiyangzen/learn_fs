<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/scsi/rc -->
# sources/test-tools/blktests/tests/scsi/rc

Purpose: shared `tests/scsi/rc` support for SCSI and sg/blk queue coverage using scsi_debug, sg devices, unmap/write-zeroes, data-lifetime, cache, atomic-write, and error-handler paths. It defines 7 shell helpers that individual tests source for requirement gates, setup/cleanup, target/device construction, and result checking.

Important APIs/types/functions: sourced libraries `common/rc`; functions `group_requires()` lines 9-11, `group_device_requires()` lines 13-15, `_have_scsi_generic()` lines 17-19, `_require_test_dev_is_scsi()` lines 21-27, `_require_test_dev_is_scsi_disk()` lines 29-35, `_get_test_dev_sg()` lines 37-39, `_test_dev_is_sata()` lines 41-43; external commands `echo`, `grep`.

Control flow: `group_requires()` uses gates `_have_root`. `group_device_requires()` uses local helpers `_require_test_dev_is_scsi`; gates `_require_test_dev_is_scsi`.

State and persistence behavior: touches state paths such as `$(<"${TEST_DEV_SYSFS}"/device/vendor)` records skip reasons in the shared harness array instead of failing unsupported hosts.

Dependencies and integration points: integrates with the blktests `scsi` suite and the shared harness; through `common/rc`; requirement gates include `_have_root`, `_require_test_dev_is_scsi`, `_have_scsi_generic`, `_have_driver sg`, `_require_test_dev_is_scsi_disk`; runtime command surface includes `echo`, `grep`.

Risks and test signals: contains loops or background/concurrent work, making cleanup and race timing important test signal is largely shell return status plus explicit comparisons in the `$FULL` log unsupported prerequisites should skip cleanly through `SKIP_REASONS`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/scsi/rc -->
