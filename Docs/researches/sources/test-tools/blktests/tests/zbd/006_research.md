<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/zbd/006 -->
# sources/test-tools/blktests/tests/zbd/006

Purpose: zoned block device coverage using blkzone, null_blk, dm, filesystems, reset/report/ioctl/sysfs, zone mapping, queue freezing, cache races, and inline encryption. This specific test is declared as: "revalidate".

Important APIs/types/functions: sourced libraries `tests/zbd/rc`; top-level variables `DESCRIPTION=revalidate`, `TIMED=1`, `CAN_BE_ZONED=1`; functions `requires()` lines 14-16, `fallback_device()` lines 18-20, `cleanup_fallback_device()` lines 22-24, `test_device()` lines 26-53; external commands `echo`, `blkzone`.

Control flow: `requires()` uses gates `_have_fio_zbd_zonemode`. `test_device()` uses commands `echo`, `blkzone`.

State and persistence behavior: touches state paths such as `$(_find_first_sequential_zone)`, `$((ZONE_STARTS[zone_idx] * 512)`, `$((ZONE_LENGTHS[zone_idx] * 512)`.

Dependencies and integration points: integrates with the blktests `zbd` suite and the shared harness; through `tests/zbd/rc`; requirement gates include `_have_fio_zbd_zonemode`; runtime command surface includes `echo`, `blkzone`.

Risks and test signals: marked `TIMED=1`, so runtime and timing jitter are expected test concerns declares `CAN_BE_ZONED=1`, so zoned-device behavior is part of the valid matrix.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/zbd/006 -->
