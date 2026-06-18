<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/throtl/004 -->
# sources/test-tools/blktests/tests/throtl/004

Purpose: block cgroup throttling coverage for cgroup v1/v2 limits, IO split accounting, delete-during-throttle, config changes, metadata priority, and iocost. This specific test is declared as: "delete disk while IO is throttled".

Important APIs/types/functions: sourced libraries `tests/throtl/rc`; top-level variables `DESCRIPTION=delete disk while IO is throttled`, `QUICK=1`; functions `set_conditions()` lines 14-16, `test()` lines 18-40; external commands `echo`, `sleep`, `grep`.

Control flow: `set_conditions()` is present and carries the file-specific action body. `test()` uses commands `echo`, `sleep`, `grep`.

State and persistence behavior: touches state paths such as `$FULL`, `$((1024 * 1024)` persists transient cgroup controller limits while IO is running writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `throtl` suite and the shared harness; through `tests/throtl/rc`; runtime command surface includes `echo`, `sleep`, `grep`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/throtl/004 -->
