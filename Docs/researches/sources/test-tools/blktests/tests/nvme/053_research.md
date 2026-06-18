<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/053 -->
# sources/test-tools/blktests/tests/nvme/053

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "test controller rescan under I/O load".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=test controller rescan under I/O load`, `TIMED=1`; functions `get_sleep_time()` lines 15-19, `rescan_controller()` lines 21-37, `test_device()` lines 39-70; external commands `echo`, `sleep`.

Control flow: `test_device()` uses local helpers `rescan_controller`; commands `echo`.

State and persistence behavior: touches state paths such as `/dev/null`, `$FULL`, `$((RANDOM % 50 + 1)`, `$((duration / 10)`, `$((duration % 10)`, `$(($(date +%s)`, `$(date +%s)`, `$(get_sleep_time)` writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; runtime command surface includes `echo`, `sleep`.

Risks and test signals: marked `TIMED=1`, so runtime and timing jitter are expected test concerns contains loops or background/concurrent work, making cleanup and race timing important test signal is largely shell return status plus explicit comparisons in the `$FULL` log.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/053 -->
