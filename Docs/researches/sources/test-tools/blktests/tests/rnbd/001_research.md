<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/rnbd/001 -->
# sources/test-tools/blktests/tests/rnbd/001

Purpose: RNBD client/server smoke and stress coverage for remote block-device mapping over loopback RDMA. This specific test is declared as: "Start Stop RNBD".

Important APIs/types/functions: sourced libraries `tests/rnbd/rc`; top-level variables `DESCRIPTION=Start Stop RNBD`, `CHECK_DMESG=1`, `QUICK=1`; functions `requires()` lines 13-16, `test()` lines 35-39; external commands `losetup`, `sleep`, `echo`.

Control flow: `requires()` uses gates `_have_rnbd`, `_have_loop`. `test()` uses commands `echo`.

State and persistence behavior: touches state paths such as `$(losetup -f)`.

Dependencies and integration points: integrates with the blktests `rnbd` suite and the shared harness; through `tests/rnbd/rc`; requirement gates include `_have_rnbd`, `_have_loop`; runtime command surface includes `losetup`, `sleep`, `echo`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/rnbd/001 -->
