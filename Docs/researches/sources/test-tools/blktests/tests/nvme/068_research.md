<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/068 -->
# sources/test-tools/blktests/tests/nvme/068

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "NVMe multipath delayed removal test".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`, `common/xfs`; top-level variables `DESCRIPTION=NVMe multipath delayed removal test`; functions `requires()` lines 14-19, `set_conditions()` lines 21-23, `_delayed_nvme_reconnect_ctrl()` lines 25-28, `test()` lines 30-113; external commands `multipath`, `sleep`, `echo`.

Control flow: `requires()` uses commands `multipath`; gates `_have_loop`, `_have_module_param_value nvme_core multipath Y`, `_require_nvme_trtype_is_fabrics`. `set_conditions()` is present and carries the file-specific action body. `test()` uses local helpers `_delayed_nvme_reconnect_ctrl`; commands `echo`.

State and persistence behavior: touches state paths such as `/sys/block/${ns}/delayed_removal_secs`, `$(_find_nvme_dev "${def_subsysnqn}")`, `$(_find_nvme_ns "${def_subsys_uuid}")`, `$(_module_use_count nvme_core)`, `$(run_xfs_io_pwritev2 /dev/"$ns" 4096)`.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`, `common/xfs`; requirement gates include `_have_loop`, `_have_module_param_value nvme_core multipath Y`, `_require_nvme_trtype_is_fabrics`; runtime command surface includes `multipath`, `sleep`, `echo`.

Risks and test signals: contains loops or background/concurrent work, making cleanup and race timing important exercises privileged kernel/device-management paths that can leave host state behind if interrupted test signal is largely shell return status plus explicit comparisons in the `$FULL` log.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/068 -->
