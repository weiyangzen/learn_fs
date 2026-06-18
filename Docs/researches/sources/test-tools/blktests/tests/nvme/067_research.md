<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/067 -->
# sources/test-tools/blktests/tests/nvme/067

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "exercise the nvme admin commands usage with io uring passthrough interfaces".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=exercise the nvme admin commands usage with io uring passthrough interfaces`, `QUICK=1`; functions `requires()` lines 8-11, `test_device()` lines 16-36; external commands `nvme`, `echo`.

Control flow: `requires()` uses gates `_have_kernel_option IO_URING`. `test_device()` uses commands `echo`.

State and persistence behavior: touches state paths such as `/dev/}`, `/dev/${devname`.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_have_kernel_option IO_URING`; runtime command surface includes `nvme`, `echo`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates exercises privileged kernel/device-management paths that can leave host state behind if interrupted.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/067 -->
