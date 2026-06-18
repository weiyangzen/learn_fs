<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/034 -->
# sources/test-tools/blktests/tests/nvme/034

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "run data verification fio job on an NVMeOF passthru controller".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=run data verification fio job on an NVMeOF passthru controller`, `TIMED=1`; functions `requires()` lines 11-15, `device_requires()` lines 17-20, `set_conditions()` lines 22-24, `test_device()` lines 26-45; external commands `fio`, `echo`.

Control flow: `requires()` uses gates `_have_kernel_option NVME_TARGET_PASSTHRU`, `_have_fio`. `device_requires()` uses gates `_require_test_dev_is_not_nvme_multipath`. `set_conditions()` is present and carries the file-specific action body. `test_device()` uses commands `echo`.

State and persistence behavior: touches state paths such as `$(_nvmet_passthru_target_connect)`.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_have_kernel_option NVME_TARGET_PASSTHRU`, `_have_fio`, `_require_test_dev_is_not_nvme_multipath`; runtime command surface includes `fio`, `echo`.

Risks and test signals: marked `TIMED=1`, so runtime and timing jitter are expected test concerns test signal is largely shell return status plus explicit comparisons in the `$FULL` log.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/034 -->
