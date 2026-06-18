<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/zbd/012 -->
# sources/test-tools/blktests/tests/zbd/012

Purpose: zoned block device coverage using blkzone, null_blk, dm, filesystems, reset/report/ioctl/sysfs, zone mapping, queue freezing, cache races, and inline encryption. This specific test is declared as: "test requeuing of zoned writes and queue freezing".

Important APIs/types/functions: sourced libraries `tests/zbd/rc`, `common/scsi_debug`; top-level variables `DESCRIPTION=test requeuing of zoned writes and queue freezing`, `TIMED=1`; functions `requires()` lines 14-17, `toggle_iosched()` lines 19-28, `test()` lines 30-91; external commands `echo`, `sleep`, `fio`.

Control flow: `requires()` uses gates `_have_fio_zbd_zonemode`, `_have_loadable_scsi_debug`. `test()` uses local helpers `toggle_iosched`; commands `echo`, `fio`.

State and persistence behavior: touches state paths such as `/sys/class/block/$`, `/dev/${SCSI_DEBUG_DEVICES`, `$(basename "$zdev")`, `$((2 * qd)`, `$((${TIMEOUT:-30}/5)` writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `zbd` suite and the shared harness; through `tests/zbd/rc`, `common/scsi_debug`; requirement gates include `_have_fio_zbd_zonemode`, `_have_loadable_scsi_debug`; runtime command surface includes `echo`, `sleep`, `fio`.

Risks and test signals: marked `TIMED=1`, so runtime and timing jitter are expected test concerns contains loops or background/concurrent work, making cleanup and race timing important.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/zbd/012 -->
