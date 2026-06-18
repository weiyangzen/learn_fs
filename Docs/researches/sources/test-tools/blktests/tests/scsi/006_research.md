<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/scsi/006 -->
# sources/test-tools/blktests/tests/scsi/006

Purpose: SCSI and sg/blk queue coverage using scsi_debug, sg devices, unmap/write-zeroes, data-lifetime, cache, atomic-write, and error-handler paths. This specific test is declared as: "toggle SCSI cache type".

Important APIs/types/functions: sourced libraries `tests/scsi/rc`; top-level variables `DESCRIPTION=toggle SCSI cache type`, `QUICK=1`, `CAN_BE_ZONED=1`; functions `device_requires()` lines 15-17, `test_device()` lines 19-52; external commands `echo`, `cat`, `grep`.

Control flow: `device_requires()` uses gates `_require_test_dev_is_scsi_disk`. `test_device()` uses commands `echo`, `cat`, `grep`.

State and persistence behavior: touches state paths such as `$(cat "$cache_type_path")`.

Dependencies and integration points: integrates with the blktests `scsi` suite and the shared harness; through `tests/scsi/rc`; requirement gates include `_require_test_dev_is_scsi_disk`; runtime command surface includes `echo`, `cat`, `grep`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates declares `CAN_BE_ZONED=1`, so zoned-device behavior is part of the valid matrix contains loops or background/concurrent work, making cleanup and race timing important test signal is largely shell return status plus explicit comparisons in the `$FULL` log.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/scsi/006 -->
