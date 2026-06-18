# sources/test-tools/fio/t/log_compression.py

## Purpose
Regression test for fio I/O log compression, ensuring compressed or asynchronously flushed log entries are neither missing nor out of order.

## Important APIs, Types, and Functions
`run_fio()` runs a null-engine sequential write workload with `--write_bw_log`, `--log_offset=1`, and `--log_compression=10K`, optionally adding `--log_store_compressed=1` and inflating the `.fz` log through fio. `check_log_file()` validates line count and monotonic offsets. `main()` runs both compressed-storage modes.

## Control Flow
For each `log_store_compressed` value, the script runs fio, inflates if needed, reads the resulting BW log, checks that the number of non-empty lines equals `1000M / 128K`, and verifies the fifth CSV field advances by block size from zero.

## State and Persistence Behavior
Writes `test_bw.log`, `test_bw.log.fz`, and `test_bw.from_fz.log` in the current directory. It does not isolate artifacts or remove outputs.

## Dependencies and Integration Points
Depends on fio's null engine, bandwidth log writer, log compression/inflation path, and subprocess execution.

## Risks
Current-directory output can collide with existing logs. It assumes log CSV field order and exact one-entry-per-I/O behavior. `subprocess.check_output()` raises on fio failure before a clean failed test report.

## Test Signals
Two passing cases prove uncompressed compressed-buffer flushing and stored-compressed inflation preserve all 8000 sequential offsets in order.
