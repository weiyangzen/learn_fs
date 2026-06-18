<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/zbd/010 -->
# sources/test-tools/blktests/tests/zbd/010

Purpose: zoned block device coverage using blkzone, null_blk, dm, filesystems, reset/report/ioctl/sysfs, zone mapping, queue freezing, cache races, and inline encryption. This specific test is declared as: "test gap zone support with F2FS".

Important APIs/types/functions: sourced libraries `tests/zbd/rc`, `common/null_blk`, `common/scsi_debug`; top-level variables `DESCRIPTION=test gap zone support with F2FS`, `QUICK=1`; functions `requires()` lines 12-20, `test()` lines 22-73; external commands `mkfs.f2fs`, `echo`, `mount`, `umount`.

Control flow: `requires()` uses commands `mkfs.f2fs`; gates `_have_fio`, `_have_driver f2fs`, `_have_module null_blk`, `_have_module_param scsi_debug zone_cap_mb`, `_have_program mkfs.f2fs`, `_have_loadable_scsi_debug`. `test()` uses commands `echo`, `mkfs.f2fs`, `mount`, `umount`.

State and persistence behavior: touches state paths such as `/dev/nullb0`, `/dev/${SCSI_DEBUG_DEVICES`, `$TMPDIR/mnt` creates filesystems or mountpoints and must unwind them during cleanup writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `zbd` suite and the shared harness; through `tests/zbd/rc`, `common/null_blk`, `common/scsi_debug`; requirement gates include `_have_fio`, `_have_driver f2fs`, `_have_module null_blk`, `_have_module_param scsi_debug zone_cap_mb`, `_have_program mkfs.f2fs`, `_have_loadable_scsi_debug`; runtime command surface includes `mkfs.f2fs`, `echo`, `mount`, `umount`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/zbd/010 -->
