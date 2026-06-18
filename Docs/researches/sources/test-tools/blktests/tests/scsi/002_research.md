<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/scsi/002 -->
# sources/test-tools/blktests/tests/scsi/002

Purpose: SCSI and sg/blk queue coverage using scsi_debug, sg devices, unmap/write-zeroes, data-lifetime, cache, atomic-write, and error-handler paths. This specific test is declared as: "perform a SG_DXFER_FROM_DEV from the /dev/sg read-write interface".

Important APIs/types/functions: sourced libraries `tests/scsi/rc`; top-level variables `DESCRIPTION=perform a SG_DXFER_FROM_DEV from the /dev/sg read-write interface`, `QUICK=1`; functions `requires()` lines 13-16, `test_device()` lines 18-25; external commands `echo`.

Control flow: `requires()` uses gates `_have_scsi_generic`, `_have_src_program sg/dxfer-from-dev`. `test_device()` uses commands `echo`.

State and persistence behavior: touches state paths such as `/dev/sg`, `/dev/$`, `$(_get_test_dev_sg)`.

Dependencies and integration points: integrates with the blktests `scsi` suite and the shared harness; through `tests/scsi/rc`; requirement gates include `_have_scsi_generic`, `_have_src_program sg/dxfer-from-dev`; runtime command surface includes `echo`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/scsi/002 -->
