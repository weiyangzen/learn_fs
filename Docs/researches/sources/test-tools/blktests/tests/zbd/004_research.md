<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/zbd/004 -->
# sources/test-tools/blktests/tests/zbd/004

Purpose: zoned block device coverage using blkzone, null_blk, dm, filesystems, reset/report/ioctl/sysfs, zone mapping, queue freezing, cache races, and inline encryption. This specific test is declared as: "write split across sequential zones".

Important APIs/types/functions: sourced libraries `tests/zbd/rc`; top-level variables `DESCRIPTION=write split across sequential zones`, `QUICK=1`, `CAN_BE_ZONED=1`; functions `fallback_device()` lines 15-17, `cleanup_fallback_device()` lines 19-21, `_check_zone_cond()` lines 23-32, `test_device()` lines 34-109; external commands `echo`, `dd`.

Control flow: `test_device()` uses local helpers `_check_zone_cond`; commands `echo`, `dd`.

State and persistence behavior: touches state paths such as `/dev/zero`, `$FULL`, `$(_find_two_contiguous_seq_zones cap_eq_len)`, `$((idx+1)`, `$(((ZONE_LENGTHS[idx] - phys_blk_sectors)`, `$((ZONE_STARTS[idx] * 512 / phys_blk_size)`, `$((ZONE_STARTS[idx+1] - phys_blk_sectors)`, `$((phys_blk_size * 2)`, `$((start_sector * 512)` writes diagnostic command output to the blktests `$FULL` log records skip reasons in the shared harness array instead of failing unsupported hosts.

Dependencies and integration points: integrates with the blktests `zbd` suite and the shared harness; through `tests/zbd/rc`; runtime command surface includes `echo`, `dd`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates declares `CAN_BE_ZONED=1`, so zoned-device behavior is part of the valid matrix contains loops or background/concurrent work, making cleanup and race timing important test signal is largely shell return status plus explicit comparisons in the `$FULL` log unsupported prerequisites should skip cleanly through `SKIP_REASONS`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/zbd/004 -->
