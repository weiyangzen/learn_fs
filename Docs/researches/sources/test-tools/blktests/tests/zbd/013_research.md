<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/zbd/013 -->
# sources/test-tools/blktests/tests/zbd/013

Purpose: zoned block device coverage using blkzone, null_blk, dm, filesystems, reset/report/ioctl/sysfs, zone mapping, queue freezing, cache races, and inline encryption. This specific test is declared as: "test stacked drivers and queue freezing".

Important APIs/types/functions: sourced libraries `tests/zbd/rc`, `common/null_blk`; top-level variables `DESCRIPTION=test stacked drivers and queue freezing`, `TIMED=1`; functions `requires()` lines 15-20, `queue_freeze_loop()` lines 25-32, `run_test()` lines 34-90, `test()` lines 92-118; external commands `echo`, `sleep`, `cat`.

Control flow: `requires()` uses gates `_have_driver dm-crypt`, `_have_driver null_blk`, `_have_fio`, `_have_program cryptsetup`. `test()` uses local helpers `run_test`; commands `echo`, `cat`.

State and persistence behavior: touches state paths such as `/sys/block/`, `/dev/nullb1`, `/dev/${zdev_basename}`, `/dev/mapper/${luks_vol_name}`, `/dev/${dmdev}`, `/dev/null`, `$(((1 << 32)`, `$(basename "$(readlink "${luksdev}")`, `$(<"${max_sectors_zdev}")`, `$(cat "${loop_pid_filename}" 2>/dev/null)` writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `zbd` suite and the shared harness; through `tests/zbd/rc`, `common/null_blk`; requirement gates include `_have_driver dm-crypt`, `_have_driver null_blk`, `_have_fio`, `_have_program cryptsetup`; runtime command surface includes `echo`, `sleep`, `cat`.

Risks and test signals: marked `TIMED=1`, so runtime and timing jitter are expected test concerns contains loops or background/concurrent work, making cleanup and race timing important.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/zbd/013 -->
