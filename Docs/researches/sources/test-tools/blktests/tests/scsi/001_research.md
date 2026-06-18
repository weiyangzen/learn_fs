<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/scsi/001 -->
# sources/test-tools/blktests/tests/scsi/001

Purpose: SCSI and sg/blk queue coverage using scsi_debug, sg devices, unmap/write-zeroes, data-lifetime, cache, atomic-write, and error-handler paths. This specific test is declared as: "try triggering a kernel GPF with 0 byte SG reads".

Important APIs/types/functions: sourced libraries `tests/scsi/rc`; top-level variables `DESCRIPTION=try triggering a kernel GPF with 0 byte SG reads`, `QUICK=1`; functions `requires()` lines 13-16, `test_device()` lines 18-26; external commands `echo`, `timeout`.

Control flow: `requires()` uses gates `_have_scsi_generic`, `_have_src_program sg/syzkaller1`. `test_device()` uses commands `echo`, `timeout`.

State and persistence behavior: touches state paths such as `/dev/$`, `$(_get_test_dev_sg)`.

Dependencies and integration points: integrates with the blktests `scsi` suite and the shared harness; through `tests/scsi/rc`; requirement gates include `_have_scsi_generic`, `_have_src_program sg/syzkaller1`; runtime command surface includes `echo`, `timeout`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/scsi/001 -->
