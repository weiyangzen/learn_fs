<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/061 -->
# sources/test-tools/blktests/tests/nvme/061

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "test fabric target teardown and setup during I/O".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=test fabric target teardown and setup during I/O`, `TIMED=1`; functions `requires()` lines 13-18, `set_conditions()` lines 20-22, `test()` lines 24-66; external commands `rdma`, `echo`, `sleep`, `cat`.

Control flow: `requires()` uses commands `rdma`; gates `_have_loop`, `_have_fio`, `_require_nvme_trtype tcp rdma fc`. `set_conditions()` is present and carries the file-specific action body. `test()` uses commands `echo`, `sleep`, `cat`.

State and persistence behavior: touches state paths such as `/sys/class/nvme-fabrics/ctl/${nvmedev}/state`, `/dev/${ns}`, `/dev/null`, `$(_find_nvme_ns "${def_subsys_uuid}")`, `$(_find_nvme_dev "${def_subsysnqn}")`, `$(cat "${state_file}")`.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_have_loop`, `_have_fio`, `_require_nvme_trtype tcp rdma fc`; runtime command surface includes `rdma`, `echo`, `sleep`, `cat`.

Risks and test signals: marked `TIMED=1`, so runtime and timing jitter are expected test concerns contains loops or background/concurrent work, making cleanup and race timing important.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/061 -->
