<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/028 -->
# sources/test-tools/blktests/tests/nvme/028

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "test NVMe list-subsys".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=test NVMe list-subsys`, `QUICK=1`; functions `requires()` lines 12-16, `set_conditions()` lines 18-20, `test()` lines 22-40; external commands `echo`, `nvme`, `grep`.

Control flow: `requires()` uses gates `_have_loop`, `_require_nvme_trtype_is_fabrics`. `set_conditions()` is present and carries the file-specific action body. `test()` uses commands `echo`, `nvme`, `grep`.

State and persistence behavior: touches state paths such as `$FULL` writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_have_loop`, `_require_nvme_trtype_is_fabrics`; runtime command surface includes `echo`, `nvme`, `grep`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important exercises privileged kernel/device-management paths that can leave host state behind if interrupted test signal is largely shell return status plus explicit comparisons in the `$FULL` log.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/028 -->
