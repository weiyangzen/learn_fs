<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/scsi/004 -->
# sources/test-tools/blktests/tests/scsi/004

Purpose: SCSI and sg/blk queue coverage using scsi_debug, sg devices, unmap/write-zeroes, data-lifetime, cache, atomic-write, and error-handler paths. This specific test is declared as: "ensure repeated TASK SET FULL results in EIO on timing out command".

Important APIs/types/functions: sourced libraries `tests/scsi/rc`, `common/scsi_debug`; top-level variables `DESCRIPTION=ensure repeated TASK SET FULL results in EIO on timing out command`, `CAN_BE_ZONED=1`; functions `requires()` lines 20-22, `test()` lines 24-49; external commands `echo`, `timeout`, `dd`, `grep`, `cat`.

Control flow: `requires()` uses gates `_have_scsi_debug`. `test()` uses commands `echo`, `timeout`, `dd`, `grep`, `cat`.

State and persistence behavior: touches state paths such as `/sys/block/${SCSI_DEBUG_DEVICES`, `/sys/bus/pseudo/drivers/scsi_debug/opts`, `/sys/bus/pseudo/drivers/scsi_debug/ndelay`, `/sys/bus/pseudo/drivers/scsi_debug/add_host`, `/dev/${SCSI_DEBUG_DEVICES`, `/dev/null`, `$(cat /sys/bus/pseudo/drivers/scsi_debug/add_host)` writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `scsi` suite and the shared harness; through `tests/scsi/rc`, `common/scsi_debug`; requirement gates include `_have_scsi_debug`; runtime command surface includes `echo`, `timeout`, `dd`, `grep`, `cat`.

Risks and test signals: declares `CAN_BE_ZONED=1`, so zoned-device behavior is part of the valid matrix contains loops or background/concurrent work, making cleanup and race timing important.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/scsi/004 -->
