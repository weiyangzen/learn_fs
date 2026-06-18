<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/srp/001 -->
# sources/test-tools/blktests/tests/srp/001

Purpose: SCSI RDMA Protocol coverage using LIO, null_blk, scsi_debug, multipath, ib_srp/srpt, and RDMA/CM or IB/CM login/logout cycles. This specific test is declared as: "Create and remove LUNs".

Important APIs/types/functions: sourced libraries `tests/srp/rc`; top-level variables `DESCRIPTION=Create and remove LUNs`, `QUICK=1`; functions `count_luns()` lines 11-23, `wait_for_luns()` lines 25-37, `test()` lines 39-42; external commands `echo`, `sleep`, `trap`.

Control flow: `test()` uses local helpers `wait_for_luns`; commands `trap`, `echo`.

State and persistence behavior: touches state paths such as `/sys/class/srp_remote_ports/`, `/sys/class/scsi_device/${h}`, `$FULL`, `$(count_luns)` writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `srp` suite and the shared harness; through `tests/srp/rc`; runtime command surface includes `echo`, `sleep`, `trap`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/srp/001 -->
