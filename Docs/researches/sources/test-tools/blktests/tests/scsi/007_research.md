<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/scsi/007 -->
# sources/test-tools/blktests/tests/scsi/007

Purpose: SCSI and sg/blk queue coverage using scsi_debug, sg devices, unmap/write-zeroes, data-lifetime, cache, atomic-write, and error-handler paths. This specific test is declared as: "Trigger the SCSI error handler".

Important APIs/types/functions: sourced libraries `tests/scsi/rc`, `common/scsi_debug`; top-level variables `DESCRIPTION=Trigger the SCSI error handler`, `QUICK=1`; functions `requires()` lines 14-16, `start_tracing()` lines 18-37, `stop_tracing()` lines 39-51, `run_test()` lines 53-92, `test()` lines 94-111; external commands `echo`, `cat`, `grep`, `timeout`, `dd`.

Control flow: `requires()` uses gates `_have_loadable_scsi_debug`. `test()` uses local helpers `run_test`; commands `echo`.

State and persistence behavior: touches state paths such as `/sys/kernel/tracing/tracing_on`, `/sys/kernel/tracing`, `/sys/module/scsi_mod/parameters/scsi_logging_level`, `/sys/class/block/$dev/queue/io_timeout`, `/sys/module/scsi_debug/parameters/delay`, `/dev/$dev`, `/dev/null`, `$FULL`, `$(<"/sys/class/block/$dev/queue/io_timeout")`, `$(_get_kernel_option HZ)`, `$((delay_s * "${freq}")` writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `scsi` suite and the shared harness; through `tests/scsi/rc`, `common/scsi_debug`; requirement gates include `_have_loadable_scsi_debug`; runtime command surface includes `echo`, `cat`, `grep`, `timeout`, `dd`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important test signal is largely shell return status plus explicit comparisons in the `$FULL` log.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/scsi/007 -->
