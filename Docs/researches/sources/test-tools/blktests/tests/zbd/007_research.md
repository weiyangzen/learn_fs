<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/zbd/007 -->
# sources/test-tools/blktests/tests/zbd/007

Purpose: zoned block device coverage using blkzone, null_blk, dm, filesystems, reset/report/ioctl/sysfs, zone mapping, queue freezing, cache races, and inline encryption. This specific test is declared as: "zone mapping between logical and container devices".

Important APIs/types/functions: sourced libraries `tests/zbd/rc`; top-level variables `DESCRIPTION=zone mapping between logical and container devices`, `CAN_BE_ZONED=1`, `QUICK=1`; functions `requires()` lines 16-18, `device_requires()` lines 20-22, `select_zones()` lines 27-41, `test_device()` lines 43-120; external commands `dmsetup`, `echo`, `blkzone`, `grep`, `dd`.

Control flow: `requires()` uses commands `dmsetup`; gates `_have_program dmsetup`. `device_requires()` uses gates `_require_test_dev_is_logical`. `test_device()` uses local helpers `select_zones`; commands `echo`, `blkzone`, `grep`, `dd`.

State and persistence behavior: touches state paths such as `/dev/zero`, `$FULL`, `$(_find_first_sequential_zone)`, `$(_find_last_sequential_zone)`, `$(_find_sequential_zone_in_middle \
				      "${zones[0]}" "${zones[1]}")`, `$((4096 * (i + 1)`, `$((container_start * 512 / bs)` writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `zbd` suite and the shared harness; through `tests/zbd/rc`; requirement gates include `_have_program dmsetup`, `_require_test_dev_is_logical`; runtime command surface includes `dmsetup`, `echo`, `blkzone`, `grep`, `dd`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates declares `CAN_BE_ZONED=1`, so zoned-device behavior is part of the valid matrix contains loops or background/concurrent work, making cleanup and race timing important exercises privileged kernel/device-management paths that can leave host state behind if interrupted test signal is largely shell return status plus explicit comparisons in the `$FULL` log.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/zbd/007 -->
