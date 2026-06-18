<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/041 -->
# sources/test-tools/blktests/tests/nvme/041

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "Create authenticated connections".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=Create authenticated connections`, `QUICK=1`; functions `requires()` lines 12-19, `set_conditions()` lines 21-23, `test()` lines 25-56; external commands `echo`, `nvme`.

Control flow: `requires()` uses gates `_have_loop`, `_have_kernel_options NVME_AUTH NVME_TARGET_AUTH`, `_require_kernel_nvme_fabrics_feature dhchap_ctrl_secret`, `_require_nvme_trtype_is_fabrics`, `_require_nvme_cli_auth`. `set_conditions()` is present and carries the file-specific action body. `test()` uses commands `echo`, `nvme`.

State and persistence behavior: touches state paths such as `/dev/null`, `$(nvme gen-dhchap-key -n "${def_subsysnqn}" 2> /dev/null)`.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_have_loop`, `_have_kernel_options NVME_AUTH NVME_TARGET_AUTH`, `_require_kernel_nvme_fabrics_feature dhchap_ctrl_secret`, `_require_nvme_trtype_is_fabrics`, `_require_nvme_cli_auth`; runtime command surface includes `echo`, `nvme`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates exercises privileged kernel/device-management paths that can leave host state behind if interrupted.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/041 -->
