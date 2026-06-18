<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/064 -->
# sources/test-tools/blktests/tests/nvme/064

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "exercise the nvme metadata usage with passthrough commands".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=exercise the nvme metadata usage with passthrough commands`, `QUICK=1`; functions `requires()` lines 14-16, `device_requires()` lines 18-21, `test_device()` lines 26-34; external commands `nvme`, `echo`.

Control flow: `requires()` is present and carries the file-specific action body. `device_requires()` is present and carries the file-specific action body. `test_device()` uses commands `echo`.

State and persistence behavior: has no durable repository state; all observable state is temporary process, device, or build output handled by the caller.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; runtime command surface includes `nvme`, `echo`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates exercises privileged kernel/device-management paths that can leave host state behind if interrupted.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/064 -->
