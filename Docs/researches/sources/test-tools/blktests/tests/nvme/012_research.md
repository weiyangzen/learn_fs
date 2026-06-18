<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/012 -->
# sources/test-tools/blktests/tests/nvme/012

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "run mkfs and data verification fio".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`, `common/xfs`; top-level variables `DESCRIPTION=run mkfs and data verification fio`, `TIMED=1`; functions `requires()` lines 13-20, `set_conditions()` lines 22-24, `test()` lines 26-48; external commands `mkfs`, `fio`, `echo`.

Control flow: `requires()` uses gates `_have_xfs`, `_have_fio`, `_have_loop`, `_require_nvme_trtype_is_fabrics`, `_require_nvme_test_img_size 350m`. `set_conditions()` is present and carries the file-specific action body. `test()` uses commands `echo`, `fio`.

State and persistence behavior: touches state paths such as `/dev/${ns}`, `$(_find_nvme_ns "${def_subsys_uuid}")` creates filesystems or mountpoints and must unwind them during cleanup.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`, `common/xfs`; requirement gates include `_have_xfs`, `_have_fio`, `_have_loop`, `_require_nvme_trtype_is_fabrics`, `_require_nvme_test_img_size 350m`; runtime command surface includes `mkfs`, `fio`, `echo`.

Risks and test signals: marked `TIMED=1`, so runtime and timing jitter are expected test concerns.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/012 -->
