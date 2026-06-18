<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/036 -->
# sources/test-tools/blktests/tests/nvme/036

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "test NVMe reset command on an NVMeOF target with a passthru controller".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=test NVMe reset command on an NVMeOF target with a passthru controller`, `QUICK=1`; functions `requires()` lines 11-14, `device_requires()` lines 16-18, `set_conditions()` lines 20-22, `test_device()` lines 24-49; external commands `echo`, `nvme`.

Control flow: `requires()` uses gates `_have_kernel_option NVME_TARGET_PASSTHRU`. `device_requires()` uses gates `_require_test_dev_is_not_nvme_multipath`. `set_conditions()` is present and carries the file-specific action body. `test_device()` uses commands `echo`, `nvme`.

State and persistence behavior: touches state paths such as `/dev/${ctrldev}`, `$FULL`, `$(_nvmet_passthru_target_connect)`, `$(_find_nvme_dev "${def_subsysnqn}")` writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_have_kernel_option NVME_TARGET_PASSTHRU`, `_require_test_dev_is_not_nvme_multipath`; runtime command surface includes `echo`, `nvme`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important exercises privileged kernel/device-management paths that can leave host state behind if interrupted test signal is largely shell return status plus explicit comparisons in the `$FULL` log.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/036 -->
