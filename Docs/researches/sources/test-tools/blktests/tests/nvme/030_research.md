<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/030 -->
# sources/test-tools/blktests/tests/nvme/030

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "ensure the discovery generation counter is updated appropriately".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=ensure the discovery generation counter is updated appropriately`, `QUICK=1`; functions `requires()` lines 12-17, `set_conditions()` lines 19-21, `test()` lines 23-69; external commands `echo`, `losetup`.

Control flow: `requires()` uses gates `_have_loop`, `_require_nvme_trtype_is_fabrics`, `_require_kernel_nvme_target`. `set_conditions()` is present and carries the file-specific action body. `test()` uses commands `echo`, `losetup`.

State and persistence behavior: touches state paths such as `$(_create_nvmet_port)`, `$(losetup -f)`, `$(_discovery_genctr "$port")`, `$(_check_genctr "${genctr}" "$port" \
			       "adding a subsystem to a port")`, `$(_check_genctr "${genctr}" "$port" "adding host to allow_hosts")`, `$(_check_genctr "${genctr}" "$port" \
			       "removing host from allow_hosts")`, `$(_check_genctr "${genctr}" "$port" \
			       "removing a subsystem from a port")`.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_have_loop`, `_require_nvme_trtype_is_fabrics`, `_require_kernel_nvme_target`; runtime command surface includes `echo`, `losetup`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/030 -->
