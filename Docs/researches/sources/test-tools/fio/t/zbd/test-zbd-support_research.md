# sources/test-tools/fio/t/zbd/test-zbd-support

## Purpose
`test-zbd-support` is fio's main shell regression suite for zoned block device behavior. It validates zonemode option parsing, sequential-zone read/write semantics, conventional/sequential mixed devices, max-open and max-active accounting, zone reset behavior, trim behavior, verify interaction, write pointer recovery, and error handling across block and libzbc engines.

## Important APIs, Types, and Functions
Harness helpers include `ioengine()`, `set_io_scheduler()`, `run_fio()`, `run_one_fio_job()`, `write_and_run_one_fio_job()`, `run_fio_on_seq()`, `prep_write()`, and log checkers `check_read()`, `check_written()`, `check_reset_count()`, and `check_log()`. Requirement helpers (`require_zbd`, `require_regular_block_dev`, `require_seq_zones`, `require_conv_zones`, `require_max_open_zones`, `require_badblock`, and others) return `SKIP_TESTCASE=255` with `SKIP_REASON`.

The test body is a numbered function suite `test1()` through `test75()`. Families include invalid option rejection, empty-zone reads, direct-I/O enforcement, random/sequential write verification, mixed conventional zone behavior, boundary rounding, `z` suffix parsing, zone reset thresholds, max-open/max-active limits, trim/open-zone accounting, verify backlog, and `continue_on_error` recovery with null_blk/scsi_debug injection.

## Control Flow and State
CLI parsing sets global modes for valgrind, libzbc, reset behavior, write-zone-remainder, selected tests, max-open override, start test, quit-on-error, zbd debug, and io_uring substitution. After sourcing `functions`, startup derives `realdev`, `disk_size`, `first_sequential_zone_sector`, `zone_size`, `sectors_per_zone`, `min_seq_write_size`, `max_open_zones`, `max_active_zones`, `unrestricted_reads`, `zone_cap_bs`, scheduler, and optional zone resets. It then enumerates selected `testN` functions, removes the per-test log, evals the test, classifies PASS/SKIP/FAIL, writes status to the log, and summarizes counts.

## Dependencies and Integration Points
The script depends heavily on `t/zbd/functions`, fio at `../../fio`, `/sys`, `dmsetup` for mapped devices, `blkzone` or libzbc, optional valgrind, timeout, null_blk/scsi_debug error injection, and kernel scheduler controls.

## Risks and Test Signals
Risks include privileged device mutation, fragile parsing of sysfs/tool output, global option arrays affecting tests, use of `eval`, typo-sensitive fio options in individual tests, time-based flakiness, and destructive zone resets. Signals are per-test log files, PASS/SKIP/FAIL classification, grep checks for expected error text, byte-count comparisons, reset-count checks, assertion/crash grep in logs, and aggregate exit status.
