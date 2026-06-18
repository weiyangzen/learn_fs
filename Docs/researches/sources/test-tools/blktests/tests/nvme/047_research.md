<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/047 -->
# sources/test-tools/blktests/tests/nvme/047

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "test different queue types for fabric transports".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`, `common/xfs`; top-level variables `DESCRIPTION=test different queue types for fabric transports`; functions `requires()` lines 12-18, `set_conditions()` lines 20-22, `test()` lines 24-52; external commands `rdma`, `echo`.

Control flow: `requires()` uses commands `rdma`; gates `_have_xfs`, `_have_fio`, `_require_nvme_trtype tcp rdma`, `_have_kver 4 21`. `set_conditions()` is present and carries the file-specific action body. `test()` uses commands `echo`.

State and persistence behavior: touches state paths such as `/dev/${ns}`, `$FULL`, `$(_find_nvme_ns "${def_subsys_uuid}")`, `$(_nvme_calc_rand_io_size 4M)` writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`, `common/xfs`; requirement gates include `_have_xfs`, `_have_fio`, `_require_nvme_trtype tcp rdma`, `_have_kver 4 21`; runtime command surface includes `rdma`, `echo`.

Risks and test signals: contains loops or background/concurrent work, making cleanup and race timing important.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/047 -->
