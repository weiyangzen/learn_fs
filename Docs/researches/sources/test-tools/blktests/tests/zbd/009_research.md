<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/zbd/009 -->
# sources/test-tools/blktests/tests/zbd/009

Purpose: zoned block device coverage using blkzone, null_blk, dm, filesystems, reset/report/ioctl/sysfs, zone mapping, queue freezing, cache races, and inline encryption. This specific test is declared as: "test gap zone support with BTRFS".

Important APIs/types/functions: sourced libraries `tests/zbd/rc`, `common/scsi_debug`; top-level variables `DESCRIPTION=test gap zone support with BTRFS`, `QUICK=1`; functions `ver_a_is_before_b()` lines 12-18, `have_good_mkfs_btrfs()` lines 21-32, `requires()` lines 34-40, `test()` lines 42-82; external commands `mkfs.btrfs`, `echo`, `mount`, `umount`.

Control flow: `requires()` uses local helpers `have_good_mkfs_btrfs`; commands `mkfs.btrfs`; gates `_have_fio`, `_have_driver btrfs`, `_have_module_param scsi_debug zone_cap_mb`, `_have_program mkfs.btrfs`, `_have_loadable_scsi_debug`. `test()` uses commands `echo`, `mkfs.btrfs`, `mount`, `umount`.

State and persistence behavior: touches state paths such as `/dev/${SCSI_DEBUG_DEVICES`, `$TMPDIR/mnt`, `$(mkfs.btrfs -V | sed 's/[^[:digit:]]*//')` creates filesystems or mountpoints and must unwind them during cleanup writes diagnostic command output to the blktests `$FULL` log records skip reasons in the shared harness array instead of failing unsupported hosts.

Dependencies and integration points: integrates with the blktests `zbd` suite and the shared harness; through `tests/zbd/rc`, `common/scsi_debug`; requirement gates include `_have_fio`, `_have_driver btrfs`, `_have_module_param scsi_debug zone_cap_mb`, `_have_program mkfs.btrfs`, `_have_loadable_scsi_debug`; runtime command surface includes `mkfs.btrfs`, `echo`, `mount`, `umount`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important unsupported prerequisites should skip cleanly through `SKIP_REASONS`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/zbd/009 -->
