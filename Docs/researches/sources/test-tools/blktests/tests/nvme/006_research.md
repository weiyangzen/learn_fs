<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/006 -->
# sources/test-tools/blktests/tests/nvme/006

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "create an NVMeOF target".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=create an NVMeOF target`, `QUICK=1`; functions `requires()` lines 12-16, `set_conditions()` lines 18-20, `test()` lines 22-32; external commands `echo`.

Control flow: `requires()` uses gates `_have_loop`, `_require_nvme_trtype_is_fabrics`. `set_conditions()` is present and carries the file-specific action body. `test()` uses commands `echo`.

State and persistence behavior: has no durable repository state; all observable state is temporary process, device, or build output handled by the caller.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_have_loop`, `_require_nvme_trtype_is_fabrics`; runtime command surface includes `echo`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/006 -->
