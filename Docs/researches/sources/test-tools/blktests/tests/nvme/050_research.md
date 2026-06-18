<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/050 -->
# sources/test-tools/blktests/tests/nvme/050

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "test nvme-pci timeout with fio jobs".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=test nvme-pci timeout with fio jobs`, `CAN_BE_ZONED=1`, `nvme_trtype=pci`; functions `requires()` lines 16-20, `test_device()` lines 22-61; external commands `timeout`, `fio`, `echo`, `grep`, `sleep`.

Control flow: `requires()` uses gates `_have_fio`, `_have_kernel_options FAIL_IO_TIMEOUT FAULT_INJECTION_DEBUG_FS`. `test_device()` uses commands `echo`, `fio`, `grep`, `sleep`.

State and persistence behavior: touches state paths such as `/sys/block/`, `/sys/kernel/debug/fail_io_timeout/probability`, `/sys/kernel/debug/fail_io_timeout/interval`, `/sys/kernel/debug/fail_io_timeout/times`, `/sys/kernel/debug/fail_io_timeout/space`, `/sys/kernel/debug/fail_io_timeout/verbose`, `/sys/bus/pci/devices/${pdev}/remove`, `/sys/bus/pci/rescan`, `$FULL`, `$(_get_pci_dev_from_blkdev)`, `$(basename "${TEST_DEV}")`, `$(nproc)` writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_have_fio`, `_have_kernel_options FAIL_IO_TIMEOUT FAULT_INJECTION_DEBUG_FS`; runtime command surface includes `timeout`, `fio`, `echo`, `grep`, `sleep`.

Risks and test signals: declares `CAN_BE_ZONED=1`, so zoned-device behavior is part of the valid matrix contains loops or background/concurrent work, making cleanup and race timing important test signal is largely shell return status plus explicit comparisons in the `$FULL` log.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/050 -->
