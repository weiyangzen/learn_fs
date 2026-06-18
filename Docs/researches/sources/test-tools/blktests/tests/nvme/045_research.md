<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/045 -->
# sources/test-tools/blktests/tests/nvme/045

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "Test re-authentication".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=Test re-authentication`, `QUICK=1`; functions `requires()` lines 12-21, `set_conditions()` lines 23-25, `test()` lines 27-115; external commands `echo`, `nvme`.

Control flow: `requires()` uses gates `_have_fio`, `_have_loop`, `_have_kernel_options NVME_AUTH NVME_TARGET_AUTH`, `_require_kernel_nvme_fabrics_feature dhchap_ctrl_secret`, `_require_nvme_trtype_is_fabrics`, `_require_nvme_cli_auth`, `_have_crypto_algorithm dh-generic`. `set_conditions()` is present and carries the file-specific action body. `test()` uses commands `echo`, `nvme`.

State and persistence behavior: touches state paths such as `/sys/class/nvme/${ctrldev}/dhchap_secret`, `/sys/class/nvme/${ctrldev}/dhchap_ctrl_secret`, `/dev/null`, `/dev/${ns}`, `$(nvme gen-dhchap-key -n "${def_subsysnqn}" 2> /dev/null)`, `$(_find_nvme_dev "${def_subsysnqn}")`, `$(nvme gen-dhchap-key --nqn "${def_subsysnqn}" 2> /dev/null)`, `$(_find_nvme_ns "${def_subsys_uuid}")`, `$(_nvme_calc_rand_io_size 4m)`.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_have_fio`, `_have_loop`, `_have_kernel_options NVME_AUTH NVME_TARGET_AUTH`, `_require_kernel_nvme_fabrics_feature dhchap_ctrl_secret`, `_require_nvme_trtype_is_fabrics`, `_require_nvme_cli_auth`, `_have_crypto_algorithm dh-generic`; runtime command surface includes `echo`, `nvme`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates exercises privileged kernel/device-management paths that can leave host state behind if interrupted.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/045 -->
