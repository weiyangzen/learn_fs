<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/throtl/005 -->
# sources/test-tools/blktests/tests/throtl/005

Purpose: block cgroup throttling coverage for cgroup v1/v2 limits, IO split accounting, delete-during-throttle, config changes, metadata priority, and iocost. This specific test is declared as: "change config with throttled IO".

Important APIs/types/functions: sourced libraries `tests/throtl/rc`; top-level variables `DESCRIPTION=change config with throttled IO`, `QUICK=1`; functions `set_conditions()` lines 13-15, `test()` lines 17-38; external commands `echo`, `sleep`.

Control flow: `set_conditions()` is present and carries the file-specific action body. `test()` uses commands `echo`, `sleep`.

State and persistence behavior: touches state paths such as `$((512 * 1024)`, `$((256 * 1024)` persists transient cgroup controller limits while IO is running.

Dependencies and integration points: integrates with the blktests `throtl` suite and the shared harness; through `tests/throtl/rc`; runtime command surface includes `echo`, `sleep`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/throtl/005 -->
