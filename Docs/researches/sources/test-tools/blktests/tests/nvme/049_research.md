<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/049 -->
# sources/test-tools/blktests/tests/nvme/049

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "basic test for uring-passthrough I/O on /dev/ngX".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=basic test for uring-passthrough I/O on /dev/ngX`, `QUICK=1`; functions `requires()` lines 11-16, `metadata_bytes_per_4k_io()` lines 18-25, `test_device()` lines 27-76; external commands `echo`, `fio`, `grep`.

Control flow: `requires()` uses gates `_have_kernel_option IO_URING`, `_have_kver 6 1`, `_have_fio_ver 3 33`. `test_device()` uses local helpers `metadata_bytes_per_4k_io`; commands `echo`, `fio`, `grep`.

State and persistence behavior: touches state paths such as `/dev/ngX`, `$(<"${TEST_DEV_SYSFS}"/queue/physical_block_size)`, `$(<"${TEST_DEV_SYSFS}"/metadata_bytes)`, `$((4096 * md_bytes / phys_bs)`, `$(_min_io "$ngdev")`, `$(metadata_bytes_per_4k_io)`, `$(fio --name=check --bs="$test_dev_bs" --size="$target_size" --filename="$ngdev" \
			    --rw=read --ioengine=io_uring_cmd 2>&1)` records skip reasons in the shared harness array instead of failing unsupported hosts.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_have_kernel_option IO_URING`, `_have_kver 6 1`, `_have_fio_ver 3 33`; runtime command surface includes `echo`, `fio`, `grep`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important test signal is largely shell return status plus explicit comparisons in the `$FULL` log unsupported prerequisites should skip cleanly through `SKIP_REASONS`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/049 -->
