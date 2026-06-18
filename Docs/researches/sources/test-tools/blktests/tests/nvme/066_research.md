<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/066 -->
# sources/test-tools/blktests/tests/nvme/066

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "Test NVMe host driver code for NVME SED operations".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=Test NVMe host driver code for NVME SED operations`, `QUICK=1`, `SED_PASSWORD=password`, `SED_NEW_PASSWORD=PASSWORD`; functions `requires()` lines 18-24, `device_requires()` lines 26-29, `nvme_sed_discover()` lines 31-35, `nvme_sed_init()` lines 37-48, `nvme_sed_lock()` lines 50-54, `nvme_sed_unlock()` lines 56-60, `nvme_sed_change_password()` lines 62-75, `nvme_sed_revert()` lines 77-86, `nvme_sed_revert_destructive()` lines 88-101, `test_device()` lines 103-173; external commands `nvme`, `echo`, `grep`.

Control flow: `requires()` uses commands `nvme`; gates `_have_kernel_option BLK_SED_OPAL`, `_have_program expect`, `_have_program nvme`, `_require_nvme_cli_sed`. `device_requires()` uses gates `_require_test_dev_is_nvme`, `_require_test_dev_support_sed`. `test_device()` uses local helpers `nvme_sed_discover`, `nvme_sed_init`, `nvme_sed_lock`, `nvme_sed_unlock`, `nvme_sed_change_password`, `nvme_sed_revert`, `nvme_sed_revert_destructive`; commands `echo`, `grep`.

State and persistence behavior: touches state paths such as `/dev/null`.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_have_kernel_option BLK_SED_OPAL`, `_have_program expect`, `_have_program nvme`, `_require_nvme_cli_sed`, `_require_test_dev_is_nvme`, `_require_test_dev_support_sed`; runtime command surface includes `nvme`, `echo`, `grep`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important exercises privileged kernel/device-management paths that can leave host state behind if interrupted test signal is largely shell return status plus explicit comparisons in the `$FULL` log.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/066 -->
