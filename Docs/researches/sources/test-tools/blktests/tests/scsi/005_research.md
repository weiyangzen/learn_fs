<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/scsi/005 -->
# sources/test-tools/blktests/tests/scsi/005

Purpose: SCSI and sg/blk queue coverage using scsi_debug, sg devices, unmap/write-zeroes, data-lifetime, cache, atomic-write, and error-handler paths. This specific test is declared as: "test SCSI device blacklisting".

Important APIs/types/functions: sourced libraries `tests/scsi/rc`, `common/scsi_debug`; top-level variables `DESCRIPTION=test SCSI device blacklisting`, `QUICK=1`; functions `requires()` lines 13-16, `test()` lines 18-48; external commands `echo`, `cat`.

Control flow: `requires()` uses gates `_have_scsi_debug`, `_have_module_param scsi_debug inq_vendor`. `test()` uses commands `echo`, `cat`.

State and persistence behavior: touches state paths such as `/sys/block/${SCSI_DEBUG_DEVICES`, `$(cat "/sys/block/${SCSI_DEBUG_DEVICES[0]}/device/vendor")`, `$(cat "/sys/block/${SCSI_DEBUG_DEVICES[0]}/device/model")`, `$(cat "/sys/block/${SCSI_DEBUG_DEVICES[0]}/device/blacklist")`.

Dependencies and integration points: integrates with the blktests `scsi` suite and the shared harness; through `tests/scsi/rc`, `common/scsi_debug`; requirement gates include `_have_scsi_debug`, `_have_module_param scsi_debug inq_vendor`; runtime command surface includes `echo`, `cat`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/scsi/005 -->
