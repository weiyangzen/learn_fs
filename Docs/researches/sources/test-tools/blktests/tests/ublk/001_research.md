<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/ublk/001 -->
# sources/test-tools/blktests/tests/ublk/001

Purpose: ublk userspace block-driver coverage for add/delete, mount, crash, recovery, and daemon-kill behavior. This specific test is declared as: "test ublk delete".

Important APIs/types/functions: sourced libraries `tests/ublk/rc`; top-level variables `DESCRIPTION=test ublk delete`; functions `_run()` lines 11-31, `test()` lines 33-47; external commands `ublk`, `echo`, `sleep`.

Control flow: `test()` uses local helpers `_run`; commands `echo`. `_run()` uses commands `echo`, `sleep`.

State and persistence behavior: touches state paths such as `/dev/ublkb0`, `$TMPDIR/img`, `$FULL` writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `ublk` suite and the shared harness; through `tests/ublk/rc`; runtime command surface includes `ublk`, `echo`, `sleep`.

Risks and test signals: contains loops or background/concurrent work, making cleanup and race timing important exercises privileged kernel/device-management paths that can leave host state behind if interrupted.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/ublk/001 -->
