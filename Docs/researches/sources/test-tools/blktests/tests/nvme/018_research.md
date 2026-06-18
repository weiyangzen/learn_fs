<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/018 -->
# sources/test-tools/blktests/tests/nvme/018

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "unit test NVMe-oF out of range access on a file backend".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=unit test NVMe-oF out of range access on a file backend`, `QUICK=1`; functions `requires()` lines 13-17, `set_conditions()` lines 19-21, `test()` lines 23-50; external commands `echo`, `blockdev`, `nvme`.

Control flow: `requires()` uses gates `_have_loop`, `_require_nvme_trtype_is_fabrics`. `set_conditions()` is present and carries the file-specific action body. `test()` uses commands `echo`, `blockdev`, `nvme`.

State and persistence behavior: touches state paths such as `/dev/${ns}`, `$FULL`, `$(_find_nvme_ns "${def_subsys_uuid}")`, `$(blockdev --getsz "/dev/${ns}")`, `$(blockdev --getbsz "/dev/${ns}")` writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_have_loop`, `_require_nvme_trtype_is_fabrics`; runtime command surface includes `echo`, `blockdev`, `nvme`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important exercises privileged kernel/device-management paths that can leave host state behind if interrupted.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/018 -->
