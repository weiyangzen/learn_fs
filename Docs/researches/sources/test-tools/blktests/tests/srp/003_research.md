<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/srp/003 -->
# sources/test-tools/blktests/tests/srp/003

Purpose: SCSI RDMA Protocol coverage using LIO, null_blk, scsi_debug, multipath, ib_srp/srpt, and RDMA/CM or IB/CM login/logout cycles. This specific test is declared as: "File I/O on top of multipath concurrently with logout and login (sq)".

Important APIs/types/functions: sourced libraries `tests/srp/rc`; top-level variables `DESCRIPTION=File I/O on top of multipath concurrently with logout and login (sq)`, `TIMED=1`; functions `requires()` lines 10-12, `test_disconnect_repeatedly()` lines 14-35, `test()` lines 37-41; external commands `multipath`, `trap`, `echo`.

Control flow: `requires()` uses gates `_have_legacy_dm`. `test()` uses local helpers `test_disconnect_repeatedly`; commands `trap`, `echo`.

State and persistence behavior: touches state paths such as `$FULL`, `$(get_bdev 0)`, `$(mountpoint 0)`, `$((10**6)` writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `srp` suite and the shared harness; through `tests/srp/rc`; requirement gates include `_have_legacy_dm`; runtime command surface includes `multipath`, `trap`, `echo`.

Risks and test signals: marked `TIMED=1`, so runtime and timing jitter are expected test concerns contains loops or background/concurrent work, making cleanup and race timing important exercises privileged kernel/device-management paths that can leave host state behind if interrupted.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/srp/003 -->
