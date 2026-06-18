<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/zbd/008 -->
# sources/test-tools/blktests/tests/zbd/008

Purpose: zoned block device coverage using blkzone, null_blk, dm, filesystems, reset/report/ioctl/sysfs, zone mapping, queue freezing, cache races, and inline encryption. This specific test is declared as: "check no stale page cache after BLKZONERESET and data read race".

Important APIs/types/functions: sourced libraries `tests/block/rc`, `common/scsi_debug`; top-level variables `DESCRIPTION=check no stale page cache after BLKZONERESET and data read race`, `TIMED=1`; functions `requires()` lines 15-19, `test()` lines 21-55; external commands `echo`, `blkzone`, `dd`.

Control flow: `requires()` uses gates `_have_loadable_scsi_debug`, `_have_module_param scsi_debug zbc`, `_have_program xfs_io`. `test()` uses commands `echo`, `blkzone`, `dd`.

State and persistence behavior: touches state paths such as `/dev/${SCSI_DEBUG_DEVICES`, `/dev/null`, `$FULL`, `$(dd if="$dev" bs=4k 2>> "$FULL" | hexdump -e '"%x"')` writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `zbd` suite and the shared harness; through `tests/block/rc`, `common/scsi_debug`; requirement gates include `_have_loadable_scsi_debug`, `_have_module_param scsi_debug zbc`, `_have_program xfs_io`; runtime command surface includes `echo`, `blkzone`, `dd`.

Risks and test signals: marked `TIMED=1`, so runtime and timing jitter are expected test concerns contains loops or background/concurrent work, making cleanup and race timing important test signal is largely shell return status plus explicit comparisons in the `$FULL` log.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/zbd/008 -->
