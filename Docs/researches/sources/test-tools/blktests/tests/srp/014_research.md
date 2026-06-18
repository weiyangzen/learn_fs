<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/srp/014 -->
# sources/test-tools/blktests/tests/srp/014

Purpose: SCSI RDMA Protocol coverage using LIO, null_blk, scsi_debug, multipath, ib_srp/srpt, and RDMA/CM or IB/CM login/logout cycles. This specific test is declared as: "Run sg_reset while I/O is ongoing".

Important APIs/types/functions: sourced libraries `tests/srp/rc`; top-level variables `DESCRIPTION=Run sg_reset while I/O is ongoing`, `TIMED=1`; functions `make_running()` lines 15-35, `make_all_running()` lines 39-51, `set_running_loop()` lines 54-63, `sg_reset_loop()` lines 66-79, `test_sg_reset()` lines 81-101, `test()` lines 103-107; external commands `sg_reset`, `echo`, `sleep`, `trap`.

Control flow: `test()` uses local helpers `test_sg_reset`; commands `trap`, `echo`.

State and persistence behavior: touches state paths such as `/sys/class/scsi_device/`, `/sys/class/block/`, `/dev/disk/by-id/dm-uuid-mpath-360014056e756c6c62300000000000000`, `/dev/}`, `/dev/null`, `$FULL`, `$(dirname "$(dirname "$sp")`, `$(<"$sp")`, `$(realpath "$dev")`, `$(basename "$(dirname "$(dirname "$h")`, `$(($(_uptime_s)`, `$(get_bdev 0)` writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `srp` suite and the shared harness; through `tests/srp/rc`; runtime command surface includes `sg_reset`, `echo`, `sleep`, `trap`.

Risks and test signals: marked `TIMED=1`, so runtime and timing jitter are expected test concerns contains loops or background/concurrent work, making cleanup and race timing important.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/srp/014 -->
