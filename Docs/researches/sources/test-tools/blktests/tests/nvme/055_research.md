<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/055 -->
# sources/test-tools/blktests/tests/nvme/055

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "Test nvme write to a loop target ns just after ns is disabled".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=Test nvme write to a loop target ns just after ns is disabled`, `QUICK=1`; functions `requires()` lines 19-24, `set_conditions()` lines 26-28, `nvmf_disable_ns_change_aen()` lines 30-70, `test()` lines 72-119; external commands `nvme`, `sleep`, `timeout`, `echo`.

Control flow: `requires()` uses gates `_have_loop`, `_require_nvme_trtype_is_loop`, `_have_kernel_option DEBUG_ATOMIC_SLEEP`. `set_conditions()` is present and carries the file-specific action body. `test()` uses local helpers `nvmf_disable_ns_change_aen`; commands `echo`, `nvme`.

State and persistence behavior: touches state paths such as `/dev/$`, `/dev/urandom`, `$FULL`, `$(nvme get-feature "$disk" --feature-id=0xB | cut -d':' -f3)`, `$(( aen_conf & 0xFEFF )`, `$(date +%s)`, `$(nvme get-feature "$disk" \
			--feature-id=0xB | cut -d':' -f3)`, `$(_find_nvme_ns "${def_subsys_uuid}")` uses configfs/sysfs to create or tear down kernel target configuration writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_have_loop`, `_require_nvme_trtype_is_loop`, `_have_kernel_option DEBUG_ATOMIC_SLEEP`; runtime command surface includes `nvme`, `sleep`, `timeout`, `echo`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important exercises privileged kernel/device-management paths that can leave host state behind if interrupted.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/055 -->
