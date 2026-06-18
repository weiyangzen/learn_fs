<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/002 -->
# sources/test-tools/blktests/tests/nvme/002

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "create many subsystems and test discovery".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=create many subsystems and test discovery`; functions `requires()` lines 12-16, `set_conditions()` lines 18-20, `test()` lines 22-53; external commands `echo`, `losetup`.

Control flow: `requires()` uses gates `_have_loop`, `_require_nvme_trtype_is_loop`. `set_conditions()` is present and carries the file-specific action body. `test()` uses commands `echo`, `losetup`.

State and persistence behavior: touches state paths such as `$(_create_nvmet_port)`, `$(losetup -f)`, `$(_check_genctr "${genctr}" "$port" \
			       "adding a subsystem to a port")`.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_have_loop`, `_require_nvme_trtype_is_loop`; runtime command surface includes `echo`, `losetup`.

Risks and test signals: contains loops or background/concurrent work, making cleanup and race timing important.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/002 -->
