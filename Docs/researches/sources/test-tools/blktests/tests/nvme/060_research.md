<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/060 -->
# sources/test-tools/blktests/tests/nvme/060

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "test nvme fabrics target reset".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=test nvme fabrics target reset`; functions `requires()` lines 11-16, `set_conditions()` lines 18-20, `nvmet_debug_trigger_reset()` lines 22-27, `nvmet_reset_loop()` lines 29-34, `test()` lines 36-64; external commands `nvme`, `rdma`, `echo`, `sleep`.

Control flow: `requires()` uses commands `rdma`; gates `_have_loop`, `_require_nvme_trtype tcp rdma fc`, `_have_kernel_option NVME_TARGET_DEBUGFS`. `set_conditions()` is present and carries the file-specific action body. `test()` uses local helpers `nvmet_reset_loop`; commands `echo`, `sleep`.

State and persistence behavior: touches state paths such as `/dev/null`, `$FULL` writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_have_loop`, `_require_nvme_trtype tcp rdma fc`, `_have_kernel_option NVME_TARGET_DEBUGFS`; runtime command surface includes `nvme`, `rdma`, `echo`, `sleep`.

Risks and test signals: contains loops or background/concurrent work, making cleanup and race timing important exercises privileged kernel/device-management paths that can leave host state behind if interrupted.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/060 -->
