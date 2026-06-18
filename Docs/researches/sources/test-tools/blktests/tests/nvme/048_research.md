<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/048 -->
# sources/test-tools/blktests/tests/nvme/048

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "Test queue count changes on reconnect".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=Test queue count changes on reconnect`; functions `requires()` lines 11-16, `set_conditions()` lines 18-20, `nvmf_check_queue_count()` lines 22-47, `set_nvmet_attr_qid_max()` lines 49-55, `set_qid_max()` lines 57-66, `test()` lines 68-102; external commands `rdma`, `cat`, `echo`, `sleep`.

Control flow: `requires()` uses commands `rdma`; gates `_have_loop`, `_require_nvme_trtype tcp rdma fc`, `_require_min_cpus 2`. `set_conditions()` is present and carries the file-specific action body. `test()` uses local helpers `set_qid_max`; commands `echo`.

State and persistence behavior: touches state paths such as `/sys/class/nvme-fabrics/ctl/`, `$(_find_nvme_dev "${subsys_name}")`, `$((queue_count + 1)`, `$(cat /sys/class/nvme-fabrics/ctl/"${nvmedev}"/queue_count)`, `$((retries - 1)` uses configfs/sysfs to create or tear down kernel target configuration records skip reasons in the shared harness array instead of failing unsupported hosts.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_have_loop`, `_require_nvme_trtype tcp rdma fc`, `_require_min_cpus 2`; runtime command surface includes `rdma`, `cat`, `echo`, `sleep`.

Risks and test signals: contains loops or background/concurrent work, making cleanup and race timing important test signal is largely shell return status plus explicit comparisons in the `$FULL` log unsupported prerequisites should skip cleanly through `SKIP_REASONS`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/048 -->
