<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/srp/012 -->
# sources/test-tools/blktests/tests/srp/012

Purpose: SCSI RDMA Protocol coverage using LIO, null_blk, scsi_debug, multipath, ib_srp/srpt, and RDMA/CM or IB/CM login/logout cycles. This specific test is declared as: "dm-mpath on top of multiple I/O schedulers".

Important APIs/types/functions: sourced libraries `tests/srp/rc`; top-level variables `DESCRIPTION=dm-mpath on top of multiple I/O schedulers`, `QUICK=1`; functions `test_io_schedulers()` lines 10-41, `test()` lines 43-46; external commands `modprobe`, `echo`, `trap`.

Control flow: `test()` uses local helpers `test_io_schedulers`; commands `trap`, `echo`.

State and persistence behavior: touches state paths such as `/dev/null`, `$FULL`, `$(uname -r)`, `$(basename "$m")`, `$(get_bdev 0)`, `$(basename "$(readlink -f "${dev}")`, `$(_io_schedulers "$dm")` loads or unloads kernel modules, so host module parameters and device lifetimes are part of the test state writes diagnostic command output to the blktests `$FULL` log records skip reasons in the shared harness array instead of failing unsupported hosts.

Dependencies and integration points: integrates with the blktests `srp` suite and the shared harness; through `tests/srp/rc`; requirement gates include `_have_legacy_dm`; runtime command surface includes `modprobe`, `echo`, `trap`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important exercises privileged kernel/device-management paths that can leave host state behind if interrupted unsupported prerequisites should skip cleanly through `SKIP_REASONS`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/srp/012 -->
