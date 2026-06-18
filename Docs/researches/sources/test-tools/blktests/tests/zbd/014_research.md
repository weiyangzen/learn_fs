<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/zbd/014 -->
# sources/test-tools/blktests/tests/zbd/014

Purpose: zoned block device coverage using blkzone, null_blk, dm, filesystems, reset/report/ioctl/sysfs, zone mapping, queue freezing, cache races, and inline encryption. This specific test is declared as: "test inline encryption and bio splitting".

Important APIs/types/functions: sourced libraries `tests/zbd/rc`, `common/null_blk`; top-level variables `DESCRIPTION=test inline encryption and bio splitting`; functions `requires()` lines 22-35, `trace_block_io()` lines 38-65, `wait_until_tracing_started()` lines 68-74, `stop_tracing()` lines 77-87, `report_stats()` lines 91-100, `devno()` lines 103-107, `run_test()` lines 109-197, `test()` lines 199-225; external commands `mkfs.f2fs`, `echo`, `grep`, `cat`, `sleep`, `umount`, `mount`, `dd`.

Control flow: `requires()` uses commands `mkfs.f2fs`; gates `_have_driver f2fs`, `_have_driver null_blk`, `_have_program fscrypt`, `_have_program mkfs.f2fs`. `test()` uses local helpers `run_test`, `stop_tracing`; commands `echo`, `umount`, `cat`.

State and persistence behavior: touches state paths such as `/sys/kernel/tracing/tracing_on`, `/sys/kernel/tracing`, `/sys/class/block/.../stat.`, `/sys/class/block/$`, `/sys/class/block/$zdev_basename/queue`, `/sys/class/block/${zdev_basename}/stat`, `/dev/nullb1`, `/dev/${zdev_basename}`, `/dev/null`, `/dev/zero`, `/etc/fscrypt.conf`, `$TMPDIR/keyfile` creates filesystems or mountpoints and must unwind them during cleanup writes diagnostic command output to the blktests `$FULL` log records skip reasons in the shared harness array instead of failing unsupported hosts.

Dependencies and integration points: integrates with the blktests `zbd` suite and the shared harness; through `tests/zbd/rc`, `common/null_blk`; requirement gates include `_have_driver f2fs`, `_have_driver null_blk`, `_have_program fscrypt`, `_have_program mkfs.f2fs`; runtime command surface includes `mkfs.f2fs`, `echo`, `grep`, `cat`, `sleep`, `umount`, `mount`, `dd`.

Risks and test signals: contains loops or background/concurrent work, making cleanup and race timing important unsupported prerequisites should skip cleanly through `SKIP_REASONS`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/zbd/014 -->
