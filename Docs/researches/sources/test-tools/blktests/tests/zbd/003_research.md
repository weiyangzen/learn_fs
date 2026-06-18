<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/zbd/003 -->
# sources/test-tools/blktests/tests/zbd/003

Purpose: zoned block device coverage using blkzone, null_blk, dm, filesystems, reset/report/ioctl/sysfs, zone mapping, queue freezing, cache races, and inline encryption. This specific test is declared as: "reset sequential required zones".

Important APIs/types/functions: sourced libraries `tests/zbd/rc`; top-level variables `DESCRIPTION=reset sequential required zones`, `QUICK=1`, `CAN_BE_ZONED=1`; functions `requires()` lines 14-16, `fallback_device()` lines 18-20, `cleanup_fallback_device()` lines 22-24, `test_device()` lines 26-87; external commands `blkzone`, `echo`, `dd`.

Control flow: `requires()` uses commands `blkzone`; gates `_have_program blkzone`. `test_device()` uses commands `echo`, `blkzone`, `dd`.

State and persistence behavior: touches state paths such as `/dev/zero`, `$FULL`, `$(_test_dev_max_open_active_zones)`, `$(_find_two_contiguous_seq_zones)`, `$((zone_idx + 1)`, `$(( 4096 / bs )`, `$((ZONE_STARTS[i] * 512 / bs)` writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `zbd` suite and the shared harness; through `tests/zbd/rc`; requirement gates include `_have_program blkzone`; runtime command surface includes `blkzone`, `echo`, `dd`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates declares `CAN_BE_ZONED=1`, so zoned-device behavior is part of the valid matrix contains loops or background/concurrent work, making cleanup and race timing important test signal is largely shell return status plus explicit comparisons in the `$FULL` log.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/zbd/003 -->
