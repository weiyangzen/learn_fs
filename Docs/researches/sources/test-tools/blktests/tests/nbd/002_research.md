<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nbd/002 -->
# sources/test-tools/blktests/tests/nbd/002

Purpose: Network Block Device coverage that exercises module loading, exported file-backed devices, partition handling, resize, disconnect, mount, and concurrent socket clearing. This specific test is declared as: "tests on partition handling for an nbd device".

Important APIs/types/functions: sourced libraries `tests/nbd/rc`; top-level variables `DESCRIPTION=tests on partition handling for an nbd device`, `QUICK=1`; functions `requires()` lines 19-22, `test()` lines 24-134; external commands `parted`, `echo`, `nbd-client`, `sleep`.

Control flow: `requires()` uses commands `parted`; gates `_have_nbd_netlink`, `_have_program parted`. `test()` uses commands `echo`, `nbd-client`, `parted`, `sleep`.

State and persistence behavior: touches state paths such as `/dev/nbd0`, `/dev/nbd0p1`, `/dev/null`, `$FULL` writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `nbd` suite and the shared harness; through `tests/nbd/rc`; requirement gates include `_have_nbd_netlink`, `_have_program parted`; runtime command surface includes `parted`, `echo`, `nbd-client`, `sleep`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important exercises privileged kernel/device-management paths that can leave host state behind if interrupted test signal is largely shell return status plus explicit comparisons in the `$FULL` log.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nbd/002 -->
