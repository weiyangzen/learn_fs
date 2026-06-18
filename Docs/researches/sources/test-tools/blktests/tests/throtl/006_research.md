<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/throtl/006 -->
# sources/test-tools/blktests/tests/throtl/006

Purpose: block cgroup throttling coverage for cgroup v1/v2 limits, IO split accounting, delete-during-throttle, config changes, metadata priority, and iocost. This specific test is declared as: "test if meta IO has higher priority than data IO".

Important APIs/types/functions: sourced libraries `tests/throtl/rc`; top-level variables `DESCRIPTION=test if meta IO has higher priority than data IO`, `QUICK=1`; functions `requires()` lines 13-16, `set_conditions()` lines 18-20, `test_meta_io()` lines 22-36, `test()` lines 38-68; external commands `mkfs.ext4`, `echo`, `mount`, `sleep`, `umount`.

Control flow: `requires()` uses commands `mkfs.ext4`; gates `_have_program mkfs.ext4`, `_have_driver ext4`. `set_conditions()` is present and carries the file-specific action body. `test()` uses local helpers `test`, `test_meta_io`; commands `echo`, `mkfs.ext4`, `mount`, `sleep`, `umount`.

State and persistence behavior: touches state paths such as `/dev/${THROTL_DEV}`, `$FULL`, `$(date +%s.%N)`, `$(echo "$end_time - $start_time" | bc)`, `$((1024 * 1024)`, `$(ps -eo pid,comm | pgrep -f "jbd2/${THROTL_DEV}" | awk '{print $1}')` creates filesystems or mountpoints and must unwind them during cleanup persists transient cgroup controller limits while IO is running writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `throtl` suite and the shared harness; through `tests/throtl/rc`; requirement gates include `_have_program mkfs.ext4`, `_have_driver ext4`; runtime command surface includes `mkfs.ext4`, `echo`, `mount`, `sleep`, `umount`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/throtl/006 -->
