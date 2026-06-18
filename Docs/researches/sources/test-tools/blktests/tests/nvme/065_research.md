<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/065 -->
# sources/test-tools/blktests/tests/nvme/065

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "test unmap write zeroes sysfs interface with nvmet devices".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`, `common/scsi_debug`; top-level variables `DESCRIPTION=test unmap write zeroes sysfs interface with nvmet devices`, `QUICK=1`, `nvmet_blkdev_type=device`; functions `requires()` lines 16-20, `set_conditions()` lines 22-24, `setup_test_device()` lines 26-46, `cleanup_test_device()` lines 48-52, `test()` lines 54-97; external commands `echo`, `cat`.

Control flow: `requires()` uses gates `_have_scsi_debug`, `_require_nvme_trtype_is_fabrics`. `set_conditions()` is present and carries the file-specific action body. `test()` uses local helpers `setup_test_device`, `cleanup_test_device`; commands `echo`, `cat`.

State and persistence behavior: touches state paths such as `/sys/block/${SCSI_DEBUG_DEVICES`, `/sys/block/$dname/queue/write_zeroes_unmap_max_hw_bytes`, `/sys/block/$dname/queue/write_zeroes_unmap_max_bytes`, `/sys/block/$dname/queue/write_zeroes_max_bytes`, `/dev/${SCSI_DEBUG_DEVICES`, `$(_create_nvmet_port)`, `$(setup_test_device lbprz=0)`, `$(cat "/sys/block/$dname/queue/write_zeroes_unmap_max_hw_bytes")`, `$(cat "/sys/block/$dname/queue/write_zeroes_unmap_max_bytes")`, `$(setup_test_device lbprz=1 lbpws=1)`, `$(cat "/sys/block/$dname/queue/write_zeroes_max_bytes")` records skip reasons in the shared harness array instead of failing unsupported hosts.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`, `common/scsi_debug`; requirement gates include `_have_scsi_debug`, `_require_nvme_trtype_is_fabrics`; runtime command surface includes `echo`, `cat`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates test signal is largely shell return status plus explicit comparisons in the `$FULL` log unsupported prerequisites should skip cleanly through `SKIP_REASONS`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/065 -->
