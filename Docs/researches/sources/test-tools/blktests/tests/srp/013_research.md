<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/srp/013 -->
# sources/test-tools/blktests/tests/srp/013

Purpose: SCSI RDMA Protocol coverage using LIO, null_blk, scsi_debug, multipath, ib_srp/srpt, and RDMA/CM or IB/CM login/logout cycles. This specific test is declared as: "Direct I/O using a discontiguous buffer".

Important APIs/types/functions: sourced libraries `tests/srp/rc`; top-level variables `DESCRIPTION=Direct I/O using a discontiguous buffer`, `QUICK=1`; functions `discontiguous_io()` lines 10-35, `test()` lines 37-40; external commands `echo`, `dd`, `trap`.

Control flow: `test()` uses local helpers `discontiguous_io`; commands `trap`, `echo`.

State and persistence behavior: touches state paths such as `$FULL`, `$(get_bdev 0)`, `$(printf "%x" $((byte ^ 0xa5)` writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `srp` suite and the shared harness; through `tests/srp/rc`; runtime command surface includes `echo`, `dd`, `trap`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/srp/013 -->
