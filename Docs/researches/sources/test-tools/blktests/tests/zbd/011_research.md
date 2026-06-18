<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/zbd/011 -->
# sources/test-tools/blktests/tests/zbd/011

Purpose: zoned block device coverage using blkzone, null_blk, dm, filesystems, reset/report/ioctl/sysfs, zone mapping, queue freezing, cache races, and inline encryption. This specific test is declared as: "DM zone resource limits stacking".

Important APIs/types/functions: sourced libraries `tests/zbd/rc`; top-level variables `DESCRIPTION=DM zone resource limits stacking`, `QUICK=1`; functions `requires()` lines 24-30, `setup_dm()` lines 35-76, `setup_concat()` lines 81-132, `check_limits()` lines 137-173, `test()` lines 284-309; external commands `dmsetup`, `echo`, `dd`.

Control flow: `requires()` uses commands `dmsetup`; gates `_have_kver 6 11`, `_have_driver dm-mod`, `_have_driver dm-crypt`, `_have_program dmsetup`, `_have_program cryptsetup`. `test()` uses local helpers `check_limits`; commands `echo`, `dmsetup`.

State and persistence behavior: touches state paths such as `/sys/block/${dname}/queue/nr_zones`, `/sys/block/${dname}/queue/chunk_sectors`, `/sys/block/${dname0}/queue/nr_zones`, `/sys/block/${dname1}/queue/nr_zones`, `/sys/block/${dname0}/queue/chunk_sectors`, `/sys/block/${devpath`, `/dev/random`, `/dev/null`, `/dev/${dname0}`, `/dev/${dname1}`, `/dev/nullb_zbd_011_1`, `/dev/nullb_zbd_011_2`.

Dependencies and integration points: integrates with the blktests `zbd` suite and the shared harness; through `tests/zbd/rc`; requirement gates include `_have_kver 6 11`, `_have_driver dm-mod`, `_have_driver dm-crypt`, `_have_program dmsetup`, `_have_program cryptsetup`; runtime command surface includes `dmsetup`, `echo`, `dd`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important exercises privileged kernel/device-management paths that can leave host state behind if interrupted test signal is largely shell return status plus explicit comparisons in the `$FULL` log.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/zbd/011 -->
