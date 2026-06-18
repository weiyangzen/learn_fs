<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/057 -->
# sources/test-tools/blktests/tests/nvme/057

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "test nvme fabrics controller ANA failover during I/O".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=test nvme fabrics controller ANA failover during I/O`; functions `requires()` lines 11-16, `set_conditions()` lines 18-20, `failback()` lines 22-35, `failover()` lines 37-50, `test()` lines 52-97; external commands `nvme`, `echo`, `sleep`.

Control flow: `requires()` uses gates `_have_loop`, `_have_fio`, `_require_nvme_trtype_is_fabrics`. `set_conditions()` is present and carries the file-specific action body. `test()` uses local helpers `failback`, `failover`; commands `echo`, `sleep`.

State and persistence behavior: touches state paths such as `/dev/${ns}`, `/dev/null`, `$FULL`, `$(( portno + 1 )`, `$(( portno + 1)`, `$(_find_nvme_ns "$def_subsys_uuid")` writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_have_loop`, `_have_fio`, `_require_nvme_trtype_is_fabrics`; runtime command surface includes `nvme`, `echo`, `sleep`.

Risks and test signals: contains loops or background/concurrent work, making cleanup and race timing important exercises privileged kernel/device-management paths that can leave host state behind if interrupted.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/057 -->
