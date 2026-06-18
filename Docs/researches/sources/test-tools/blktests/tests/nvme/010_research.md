<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/010 -->
# sources/test-tools/blktests/tests/nvme/010

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "run data verification fio job".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=run data verification fio job`, `TIMED=1`; functions `requires()` lines 12-17, `set_conditions()` lines 19-21, `test()` lines 23-44; external commands `fio`, `echo`.

Control flow: `requires()` uses gates `_have_fio`, `_have_loop`, `_require_nvme_trtype_is_fabrics`. `set_conditions()` is present and carries the file-specific action body. `test()` uses commands `echo`.

State and persistence behavior: touches state paths such as `/dev/${ns}`, `$(_find_nvme_ns "${def_subsys_uuid}")`.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_have_fio`, `_have_loop`, `_require_nvme_trtype_is_fabrics`; runtime command surface includes `fio`, `echo`.

Risks and test signals: marked `TIMED=1`, so runtime and timing jitter are expected test concerns.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/010 -->
