<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/ublk/005 -->
# sources/test-tools/blktests/tests/ublk/005

Purpose: ublk userspace block-driver coverage for add/delete, mount, crash, recovery, and daemon-kill behavior. This specific test is declared as: "test ublk recovery with one time daemon kill".

Important APIs/types/functions: sourced libraries `tests/ublk/rc`; top-level variables `DESCRIPTION=test ublk recovery with one time daemon kill`; functions `_run()` lines 13-61, `test()` lines 63-77; external commands `ublk`, `echo`, `sleep`.

Control flow: `test()` uses local helpers `_run`; commands `echo`. `_run()` uses commands `echo`, `sleep`.

State and persistence behavior: touches state paths such as `/dev/ublkb0`, `$TMPDIR/img`, `$FULL`, `$(_get_ublk_daemon_pid 0)`, `$(_get_ublk_dev_state 0)` writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `ublk` suite and the shared harness; through `tests/ublk/rc`; runtime command surface includes `ublk`, `echo`, `sleep`.

Risks and test signals: contains loops or background/concurrent work, making cleanup and race timing important exercises privileged kernel/device-management paths that can leave host state behind if interrupted.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/ublk/005 -->
