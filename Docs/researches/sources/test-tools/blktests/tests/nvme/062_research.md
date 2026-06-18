<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/062 -->
# sources/test-tools/blktests/tests/nvme/062

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "Create TLS-encrypted connections".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=Create TLS-encrypted connections`, `QUICK=1`; functions `requires()` lines 12-21, `set_conditions()` lines 23-25, `test()` lines 27-94; external commands `echo`, `nvme`.

Control flow: `requires()` uses gates `_have_loop`, `_have_kernel_options NVME_TCP_TLS NVME_TARGET_TCP_TLS`, `_require_kernel_nvme_fabrics_feature tls`, `_require_nvme_trtype tcp`, `_require_nvme_cli_tls`, `_have_libnvme_ver 1 11`, `_have_systemd_tlshd_service`. `set_conditions()` is present and carries the file-specific action body. `test()` uses commands `echo`, `nvme`.

State and persistence behavior: touches state paths such as `/dev/null`, `$(nvme gen-tls-key -n "${def_hostnqn}" -c "${def_subsysnqn}" -m 1 -I 1 -i 2> /dev/null)`, `$(_find_nvme_dev "${def_subsysnqn}")`.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_have_loop`, `_have_kernel_options NVME_TCP_TLS NVME_TARGET_TCP_TLS`, `_require_kernel_nvme_fabrics_feature tls`, `_require_nvme_trtype tcp`, `_require_nvme_cli_tls`, `_have_libnvme_ver 1 11`, `_have_systemd_tlshd_service`; runtime command surface includes `echo`, `nvme`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates exercises privileged kernel/device-management paths that can leave host state behind if interrupted.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/062 -->
