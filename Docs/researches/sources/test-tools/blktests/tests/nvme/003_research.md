<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/003 -->
# sources/test-tools/blktests/tests/nvme/003

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "test if we're sending keep-alives to a discovery controller".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=test if we're sending keep-alives to a discovery controller`, `QUICK=1`; functions `requires()` lines 13-18, `set_conditions()` lines 20-22, `test()` lines 24-50; external commands `echo`, `sleep`, `grep`.

Control flow: `requires()` uses gates `_have_loop`, `_require_nvme_trtype_is_fabrics`, `_have_writeable_kmsg`. `set_conditions()` is present and carries the file-specific action body. `test()` uses commands `echo`, `sleep`, `grep`.

State and persistence behavior: has no durable repository state; all observable state is temporary process, device, or build output handled by the caller.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_have_loop`, `_require_nvme_trtype_is_fabrics`, `_have_writeable_kmsg`; runtime command surface includes `echo`, `sleep`, `grep`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important test signal is largely shell return status plus explicit comparisons in the `$FULL` log.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/003 -->
