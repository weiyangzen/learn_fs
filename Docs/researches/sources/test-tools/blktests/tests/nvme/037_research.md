<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/037 -->
# sources/test-tools/blktests/tests/nvme/037

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "test deletion of NVMeOF passthru controllers immediately after setup".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=test deletion of NVMeOF passthru controllers immediately after setup`; functions `requires()` lines 10-13, `device_requires()` lines 15-17, `set_conditions()` lines 19-21, `test_device()` lines 23-48; external commands `echo`.

Control flow: `requires()` uses gates `_have_kernel_option NVME_TARGET_PASSTHRU`. `device_requires()` uses gates `_require_test_dev_is_not_nvme_multipath`. `set_conditions()` is present and carries the file-specific action body. `test_device()` uses commands `echo`.

State and persistence behavior: touches state paths such as `$(_nvmet_passthru_target_connect \
				--subsysnqn "${subsys}${i}")` writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_have_kernel_option NVME_TARGET_PASSTHRU`, `_require_test_dev_is_not_nvme_multipath`; runtime command surface includes `echo`.

Risks and test signals: contains loops or background/concurrent work, making cleanup and race timing important test signal is largely shell return status plus explicit comparisons in the `$FULL` log.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/037 -->
