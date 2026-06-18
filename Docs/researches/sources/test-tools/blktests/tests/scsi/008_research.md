<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/scsi/008 -->
# sources/test-tools/blktests/tests/scsi/008

Purpose: SCSI and sg/blk queue coverage using scsi_debug, sg devices, unmap/write-zeroes, data-lifetime, cache, atomic-write, and error-handler paths. This specific test is declared as: "test block data lifetime support".

Important APIs/types/functions: sourced libraries `tests/scsi/rc`, `common/scsi_debug`; top-level variables `DESCRIPTION=test block data lifetime support`, `QUICK=1`; functions `requires()` lines 11-17, `submit_io()` lines 19-56, `test()` lines 58-88; external commands `echo`, `fio`, `grep`.

Control flow: `requires()` uses gates `_have_scsi_debug_group_number_stats`, `_have_fio_ver 3 37`. `test()` uses local helpers `submit_io`; commands `echo`.

State and persistence behavior: touches state paths such as `/sys/bus/pseudo/drivers/scsi_debug/group_number_stats`, `/sys/vm/drop_caches`, `/dev/${SCSI_DEBUG_DEVICES`, `/proc/sys/vm/drop_caches`, `$((1 - direct_io)` writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `scsi` suite and the shared harness; through `tests/scsi/rc`, `common/scsi_debug`; requirement gates include `_have_scsi_debug_group_number_stats`, `_have_fio_ver 3 37`; runtime command surface includes `echo`, `fio`, `grep`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/scsi/008 -->
