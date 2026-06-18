<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/059 -->
# sources/test-tools/blktests/tests/nvme/059

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "test atomic writes".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`, `common/xfs`; top-level variables `DESCRIPTION=test atomic writes`, `QUICK=1`; functions `requires()` lines 13-17, `device_requires()` lines 19-21, `test_device()` lines 23-146; external commands `nvme`, `echo`, `cat`, `grep`.

Control flow: `requires()` uses commands `nvme`; gates `_have_program nvme`, `_have_xfs_io_atomic_write`. `device_requires()` uses gates `_require_device_support_atomic_writes`. `test_device()` uses commands `echo`, `cat`, `nvme`, `grep`.

State and persistence behavior: touches state paths such as `$(cat "$queue_path"/logical_block_size)`, `$(cat "$queue_path"/max_hw_sectors_kb)`, `$(( "$sysfs_max_hw_sectors_kb" * 1024 )`, `$(cat "$queue_path"/atomic_write_max_bytes)`, `$(cat "$queue_path"/atomic_write_unit_max_bytes)`, `$(cat "$queue_path"/atomic_write_unit_min_bytes)`, `$(nvme id-ns /dev/"${ns_dev}" | grep nsfeat | awk '{ print $3}')`, `$((("$nvme_nsfeat" & 0x2)`, `$(nvme id-ns /dev/"$ns_dev" | grep nawupf | awk '{ print $3}')`, `$(( ("$nvme_awupf" + 1)`, `$(nvme id-ctrl /dev/"${ctrl_dev}" | grep awupf | awk '{ print $3}')`, `$(run_xfs_io_xstat /dev/"$ns_dev" "stat.atomic_write_unit_max")`.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`, `common/xfs`; requirement gates include `_have_program nvme`, `_have_xfs_io_atomic_write`, `_require_device_support_atomic_writes`; runtime command surface includes `nvme`, `echo`, `cat`, `grep`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important exercises privileged kernel/device-management paths that can leave host state behind if interrupted.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/059 -->
