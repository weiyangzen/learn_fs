<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/srp/007 -->
# sources/test-tools/blktests/tests/srp/007

Purpose: SCSI RDMA Protocol coverage using LIO, null_blk, scsi_debug, multipath, ib_srp/srpt, and RDMA/CM or IB/CM login/logout cycles. This specific test is declared as: "Direct I/O with large transfer sizes, cmd_sg_entries=1 and bs=4M".

Important APIs/types/functions: sourced libraries `tests/srp/rc`; top-level variables `DESCRIPTION=Direct I/O with large transfer sizes, cmd_sg_entries=1 and bs=4M`, `QUICK=1`; functions `test_low_sg_size()` lines 10-22, `test()` lines 24-27; external commands `trap`, `echo`.

Control flow: `test()` uses local helpers `test_low_sg_size`; commands `trap`, `echo`.

State and persistence behavior: touches state paths such as `$FULL`, `$(get_bdev 0)`, `$((10**6)` writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `srp` suite and the shared harness; through `tests/srp/rc`; runtime command surface includes `trap`, `echo`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/srp/007 -->
