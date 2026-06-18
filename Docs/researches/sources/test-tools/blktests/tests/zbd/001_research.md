<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/zbd/001 -->
# sources/test-tools/blktests/tests/zbd/001

Purpose: zoned block device coverage using blkzone, null_blk, dm, filesystems, reset/report/ioctl/sysfs, zone mapping, queue freezing, cache races, and inline encryption. This specific test is declared as: "sysfs and ioctl".

Important APIs/types/functions: sourced libraries `tests/zbd/rc`; top-level variables `DESCRIPTION=sysfs and ioctl`, `QUICK=1`, `CAN_BE_ZONED=1`; functions `requires()` lines 14-16, `fallback_device()` lines 18-20, `cleanup_fallback_device()` lines 22-24, `test_device()` lines 26-74; external commands `echo`.

Control flow: `requires()` uses gates `_have_src_program zbdioctl`. `test_device()` uses commands `echo`.

State and persistence behavior: touches state paths such as `$FULL`, `$(( (capacity - 1)`, `$(src/zbdioctl -s "${TEST_DEV}")`, `$(src/zbdioctl -n "${TEST_DEV}")` writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `zbd` suite and the shared harness; through `tests/zbd/rc`; requirement gates include `_have_src_program zbdioctl`; runtime command surface includes `echo`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates declares `CAN_BE_ZONED=1`, so zoned-device behavior is part of the valid matrix contains loops or background/concurrent work, making cleanup and race timing important test signal is largely shell return status plus explicit comparisons in the `$FULL` log.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/zbd/001 -->
