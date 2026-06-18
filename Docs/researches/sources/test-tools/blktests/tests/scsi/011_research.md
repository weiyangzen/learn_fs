<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/scsi/011 -->
# sources/test-tools/blktests/tests/scsi/011

Purpose: SCSI and sg/blk queue coverage using scsi_debug, sg devices, unmap/write-zeroes, data-lifetime, cache, atomic-write, and error-handler paths. This specific test is declared as: "test data lifetime propagation".

Important APIs/types/functions: sourced libraries `tests/scsi/rc`, `common/null_blk`, `common/scsi_debug`; top-level variables `DESCRIPTION=test data lifetime propagation`, `QUICK=1`; functions `requires()` lines 12-21, `run_test()` lines 23-47, `test()` lines 49-74; external commands `mkfs.f2fs`, `mount`, `echo`, `umount`.

Control flow: `requires()` uses commands `mkfs.f2fs`; gates `_have_fio`, `_have_driver f2fs`, `_have_kver 6 10`, `_have_program mkfs.f2fs`, `_have_scsi_debug_group_number_stats`. `test()` uses local helpers `run_test`; commands `echo`, `umount`.

State and persistence behavior: touches state paths such as `/sys/bus/pseudo/drivers/scsi_debug/group_number_stats`, `/dev/${SCSI_DEBUG_DEVICES`, `$TMPDIR/mnt` creates filesystems or mountpoints and must unwind them during cleanup writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `scsi` suite and the shared harness; through `tests/scsi/rc`, `common/null_blk`, `common/scsi_debug`; requirement gates include `_have_fio`, `_have_driver f2fs`, `_have_kver 6 10`, `_have_program mkfs.f2fs`, `_have_scsi_debug_group_number_stats`; runtime command surface includes `mkfs.f2fs`, `mount`, `echo`, `umount`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/scsi/011 -->
