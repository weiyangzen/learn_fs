<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/005 -->
# sources/test-tools/blktests/tests/nvme/005

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "reset local loopback target".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=reset local loopback target`, `QUICK=1`; functions `requires()` lines 13-18, `set_conditions()` lines 20-22, `test()` lines 24-44; external commands `multipath`, `echo`.

Control flow: `requires()` uses commands `multipath`; gates `_have_loop`, `_have_module_param_value nvme_core multipath Y`, `_require_nvme_trtype_is_fabrics`. `set_conditions()` is present and carries the file-specific action body. `test()` uses commands `echo`.

State and persistence behavior: touches state paths such as `/sys/class/nvme/${nvmedev}/reset_controller`, `$(_find_nvme_dev "${def_subsysnqn}")`.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_have_loop`, `_have_module_param_value nvme_core multipath Y`, `_require_nvme_trtype_is_fabrics`; runtime command surface includes `multipath`, `echo`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important exercises privileged kernel/device-management paths that can leave host state behind if interrupted.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/005 -->
