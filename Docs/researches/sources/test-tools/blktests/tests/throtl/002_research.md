<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/throtl/002 -->
# sources/test-tools/blktests/tests/throtl/002

Purpose: block cgroup throttling coverage for cgroup v1/v2 limits, IO split accounting, delete-during-throttle, config changes, metadata priority, and iocost. This specific test is declared as: "iops limit over IO split".

Important APIs/types/functions: sourced libraries `tests/throtl/rc`; top-level variables `DESCRIPTION=iops limit over IO split`, `QUICK=1`; functions `set_conditions()` lines 13-15, `test()` lines 17-46; external commands `echo`.

Control flow: `set_conditions()` is present and carries the file-specific action body. `test()` uses commands `echo`.

State and persistence behavior: touches state paths such as `$(_get_page_size)`, `$(($(_throtl_get_max_io_size)`, `$((page_size / 1024)`, `$((iops * page_size)`.

Dependencies and integration points: integrates with the blktests `throtl` suite and the shared harness; through `tests/throtl/rc`; runtime command surface includes `echo`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/throtl/002 -->
