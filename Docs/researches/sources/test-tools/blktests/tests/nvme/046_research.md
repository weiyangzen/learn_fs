<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/046 -->
# sources/test-tools/blktests/tests/nvme/046

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "basic test for unprivileged passthrough on /dev/ngX".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=basic test for unprivileged passthrough on /dev/ngX`, `QUICK=1`; functions `requires()` lines 11-15, `test_device()` lines 17-53; external commands `echo`, `chmod`, `nvme`.

Control flow: `requires()` uses gates `_require_normal_user`, `_have_kver 6 2`. `test_device()` uses commands `echo`, `chmod`, `nvme`.

State and persistence behavior: touches state paths such as `/dev/ngX`, `$(stat -c "%a" "$ngdev")`, `$(_test_dev_nvme_nsid)` writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_require_normal_user`, `_have_kver 6 2`; runtime command surface includes `echo`, `chmod`, `nvme`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important exercises privileged kernel/device-management paths that can leave host state behind if interrupted.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/046 -->
