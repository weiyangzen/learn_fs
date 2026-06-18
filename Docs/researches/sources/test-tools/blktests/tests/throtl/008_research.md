<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/throtl/008 -->
# sources/test-tools/blktests/tests/throtl/008

Purpose: block cgroup throttling coverage for cgroup v1/v2 limits, IO split accounting, delete-during-throttle, config changes, metadata priority, and iocost. This specific test is declared as: "test cgroup iocost controller limits".

Important APIs/types/functions: sourced libraries `tests/throtl/rc`, `common/fio`; top-level variables `DESCRIPTION=test cgroup iocost controller limits`; functions `requires()` lines 12-15, `set_conditions()` lines 17-19, `run_test()` lines 21-79, `test()` lines 81-107; external commands `fio`, `echo`, `cat`.

Control flow: `requires()` uses gates `_have_fio`, `_have_kernel_option BLK_CGROUP_IOCOST`. `set_conditions()` is present and carries the file-specific action body. `test()` uses local helpers `run_test`; commands `echo`.

State and persistence behavior: touches state paths such as `/sys/block/${THROTL_DEV}/dev`, `/dev/${THROTL_DEV}`, `$TMPDIR/fio_perf`, `$FULL`, `$(<"/sys/block/${THROTL_DEV}/dev")`, `$(_cgroup2_base_dir)`, `$(echo "$read_iops < 90 || $read_iops > 110" | bc -l)`, `$(echo "$write_iops < 8 || $write_iops > 12" | bc -l)` persists transient cgroup controller limits while IO is running writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `throtl` suite and the shared harness; through `tests/throtl/rc`, `common/fio`; requirement gates include `_have_fio`, `_have_kernel_option BLK_CGROUP_IOCOST`; runtime command surface includes `fio`, `echo`, `cat`.

Risks and test signals: contains loops or background/concurrent work, making cleanup and race timing important test signal is largely shell return status plus explicit comparisons in the `$FULL` log.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/throtl/008 -->
