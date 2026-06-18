<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/014 -->
# sources/test-tools/blktests/tests/nvme/014

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "flush a command from host".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=flush a command from host`, `QUICK=1`; functions `requires()` lines 12-16, `set_conditions()` lines 18-20, `test()` lines 22-52; external commands `echo`, `blockdev`, `dd`, `nvme`.

Control flow: `requires()` uses gates `_have_loop`, `_require_nvme_trtype_is_fabrics`. `set_conditions()` is present and carries the file-specific action body. `test()` uses commands `echo`, `blockdev`, `dd`, `nvme`.

State and persistence behavior: touches state paths such as `/dev/${ns}`, `/dev/urandom`, `$(_find_nvme_ns "${def_subsys_uuid}")`, `$(blockdev --getsize64 "/dev/${ns}")`, `$(blockdev --getbsz "/dev/${ns}")`, `$((size / bs)`.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_have_loop`, `_require_nvme_trtype_is_fabrics`; runtime command surface includes `echo`, `blockdev`, `dd`, `nvme`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates exercises privileged kernel/device-management paths that can leave host state behind if interrupted.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/014 -->
