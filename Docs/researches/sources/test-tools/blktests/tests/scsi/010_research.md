<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/scsi/010 -->
# sources/test-tools/blktests/tests/scsi/010

Purpose: SCSI and sg/blk queue coverage using scsi_debug, sg devices, unmap/write-zeroes, data-lifetime, cache, atomic-write, and error-handler paths. This specific test is declared as: "test unmap write zeroes sysfs interface with scsi devices".

Important APIs/types/functions: sourced libraries `tests/scsi/rc`, `common/scsi_debug`; top-level variables `DESCRIPTION=test unmap write zeroes sysfs interface with scsi devices`, `QUICK=1`; functions `requires()` lines 14-16, `setup_test_device()` lines 18-28, `test()` lines 30-84; external commands `echo`, `cat`.

Control flow: `requires()` uses gates `_have_scsi_debug`. `test()` uses local helpers `setup_test_device`; commands `echo`, `cat`.

State and persistence behavior: touches state paths such as `/sys/block/${SCSI_DEBUG_DEVICES`, `$(cat "/sys/block/${SCSI_DEBUG_DEVICES[0]}/queue/write_zeroes_unmap_max_hw_bytes")`, `$(cat "/sys/block/${SCSI_DEBUG_DEVICES[0]}/queue/write_zeroes_unmap_max_bytes")`, `$(cat "/sys/block/${SCSI_DEBUG_DEVICES[0]}/queue/write_zeroes_max_bytes")` records skip reasons in the shared harness array instead of failing unsupported hosts.

Dependencies and integration points: integrates with the blktests `scsi` suite and the shared harness; through `tests/scsi/rc`, `common/scsi_debug`; requirement gates include `_have_scsi_debug`; runtime command surface includes `echo`, `cat`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates test signal is largely shell return status plus explicit comparisons in the `$FULL` log unsupported prerequisites should skip cleanly through `SKIP_REASONS`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/scsi/010 -->
