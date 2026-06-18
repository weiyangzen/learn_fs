<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/scsi/009 -->
# sources/test-tools/blktests/tests/scsi/009

Purpose: SCSI and sg/blk queue coverage using scsi_debug, sg devices, unmap/write-zeroes, data-lifetime, cache, atomic-write, and error-handler paths. This specific test is declared as: "test scsi atomic writes".

Important APIs/types/functions: sourced libraries `tests/scsi/rc`, `common/scsi_debug`, `common/xfs`; top-level variables `DESCRIPTION=test scsi atomic writes`, `QUICK=1`; functions `requires()` lines 14-17, `device_requires()` lines 19-21, `fallback_device()` lines 23-32, `cleanup_fallback_device()` lines 34-36, `test_device()` lines 38-183; external commands `echo`.

Control flow: `requires()` uses gates `_have_scsi_debug`, `_have_xfs_io_atomic_write`. `device_requires()` uses gates `_require_device_support_atomic_writes`. `test_device()` uses commands `echo`.

State and persistence behavior: touches state paths such as `/sys/module/scsi_debug/parameters/atomic_wr_max_length`, `/sys/module/scsi_debug/parameters/atomic_wr_gran`, `/dev/${SCSI_DEBUG_DEVICES`, `$(< "${TEST_DEV_SYSFS}"/queue/logical_block_size)`, `$(< "${TEST_DEV_SYSFS}"/queue/max_hw_sectors_kb)`, `$(( "$sysfs_max_hw_sectors_kb" * 1024 )`, `$(< "${TEST_DEV_SYSFS}"/queue/atomic_write_max_bytes)`, `$(< "${TEST_DEV_SYSFS}"/queue/atomic_write_unit_max_bytes)`, `$(< "${TEST_DEV_SYSFS}"/queue/atomic_write_unit_min_bytes)`, `$(< /sys/module/scsi_debug/parameters/atomic_wr_max_length)`, `$(< /sys/module/scsi_debug/parameters/atomic_wr_gran)`, `$(( "$scsi_debug_atomic_wr_max_length" * "$sysfs_logical_block_size" )`.

Dependencies and integration points: integrates with the blktests `scsi` suite and the shared harness; through `tests/scsi/rc`, `common/scsi_debug`, `common/xfs`; requirement gates include `_have_scsi_debug`, `_have_xfs_io_atomic_write`, `_require_device_support_atomic_writes`; runtime command surface includes `echo`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/scsi/009 -->
