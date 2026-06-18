<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/035 -->
# sources/test-tools/blktests/tests/nvme/035

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "run mkfs and data verification fio job on an NVMeOF passthru controller".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`, `common/xfs`; top-level variables `DESCRIPTION=run mkfs and data verification fio job on an NVMeOF passthru controller`, `TIMED=1`; functions `requires()` lines 12-17, `device_requires()` lines 19-24, `set_conditions()` lines 26-28, `test_device()` lines 30-49; external commands `mkfs`, `fio`, `echo`.

Control flow: `requires()` uses gates `_have_kernel_option NVME_TARGET_PASSTHRU`, `_have_xfs`, `_have_fio`. `device_requires()` uses gates `_require_test_dev_is_not_nvme_multipath`, `_require_test_dev_size`. `set_conditions()` is present and carries the file-specific action body. `test_device()` uses commands `echo`, `fio`.

State and persistence behavior: touches state paths such as `$(_nvmet_passthru_target_connect)` creates filesystems or mountpoints and must unwind them during cleanup.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`, `common/xfs`; requirement gates include `_have_kernel_option NVME_TARGET_PASSTHRU`, `_have_xfs`, `_have_fio`, `_require_test_dev_is_not_nvme_multipath`, `_require_test_dev_size`; runtime command surface includes `mkfs`, `fio`, `echo`.

Risks and test signals: marked `TIMED=1`, so runtime and timing jitter are expected test concerns test signal is largely shell return status plus explicit comparisons in the `$FULL` log.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/035 -->
