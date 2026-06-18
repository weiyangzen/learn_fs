<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/rnbd/002 -->
# sources/test-tools/blktests/tests/rnbd/002

Purpose: RNBD client/server smoke and stress coverage for remote block-device mapping over loopback RDMA. This specific test is declared as: "Start Stop RNBD repeatedly".

Important APIs/types/functions: sourced libraries `tests/rnbd/rc`; top-level variables `DESCRIPTION=Start Stop RNBD repeatedly`, `CHECK_DMESG=1`, `QUICK=1`; functions `requires()` lines 19-22, `test()` lines 43-47; external commands `losetup`, `echo`.

Control flow: `requires()` uses gates `_have_rnbd`, `_have_loop`. `test()` uses commands `echo`.

State and persistence behavior: touches state paths such as `/dev/null`, `$(losetup -f)`.

Dependencies and integration points: integrates with the blktests `rnbd` suite and the shared harness; through `tests/rnbd/rc`; requirement gates include `_have_rnbd`, `_have_loop`; runtime command surface includes `losetup`, `echo`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/rnbd/002 -->
