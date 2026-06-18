<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/063 -->
# sources/test-tools/blktests/tests/nvme/063

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "Create authenticated TCP connections with secure concatenation".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=Create authenticated TCP connections with secure concatenation`, `QUICK=1`; functions `requires()` lines 12-22, `set_conditions()` lines 24-26, `test()` lines 28-107; external commands `echo`, `nvme`.

Control flow: `requires()` uses gates `_have_loop`, `_have_kernel_options NVME_AUTH NVME_TCP_TLS NVME_TARGET_AUTH \`, `_require_kernel_nvme_fabrics_feature dhchap_ctrl_secret`, `_require_kernel_nvme_fabrics_feature concat`, `_require_nvme_trtype tcp`, `_require_nvme_cli_auth`, `_have_systemd_tlshd_service`. `set_conditions()` is present and carries the file-specific action body. `test()` uses commands `echo`, `nvme`.

State and persistence behavior: touches state paths such as `/dev/null`, `/dev/${ctrl}`, `$(nvme gen-dhchap-key -m 1 -n "${def_hostnqn}" 2> /dev/null)`, `$(_find_nvme_dev "${def_subsysnqn}")`, `$(_nvme_ctrl_tls_key "$ctrl" || true)`, `$(nvme gen-dhchap-key -m 2 -n "${def_hostnqn}" 2> /dev/null)`.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_have_loop`, `_have_kernel_options NVME_AUTH NVME_TCP_TLS NVME_TARGET_AUTH \`, `_require_kernel_nvme_fabrics_feature dhchap_ctrl_secret`, `_require_kernel_nvme_fabrics_feature concat`, `_require_nvme_trtype tcp`, `_require_nvme_cli_auth`, `_have_systemd_tlshd_service`; runtime command surface includes `echo`, `nvme`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important exercises privileged kernel/device-management paths that can leave host state behind if interrupted test signal is largely shell return status plus explicit comparisons in the `$FULL` log.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/063 -->
