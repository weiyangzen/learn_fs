<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/040 -->
# sources/test-tools/blktests/tests/nvme/040

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "test nvme fabrics controller reset/disconnect operation during I/O".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=test nvme fabrics controller reset/disconnect operation during I/O`; functions `requires()` lines 12-17, `set_conditions()` lines 19-21, `test()` lines 23-58; external commands `nvme`, `echo`, `fio`, `sleep`.

Control flow: `requires()` uses gates `_have_loop`, `_have_fio`, `_require_nvme_trtype_is_fabrics`. `set_conditions()` is present and carries the file-specific action body. `test()` uses commands `echo`, `fio`, `sleep`.

State and persistence behavior: touches state paths such as `/dev/${ns}`, `/dev/null`, `$(_find_nvme_dev "${def_subsysnqn}")`, `$(_find_nvme_ns "${def_subsys_uuid}")`.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_have_loop`, `_have_fio`, `_require_nvme_trtype_is_fabrics`; runtime command surface includes `nvme`, `echo`, `fio`, `sleep`.

Risks and test signals: contains loops or background/concurrent work, making cleanup and race timing important exercises privileged kernel/device-management paths that can leave host state behind if interrupted.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/040 -->
