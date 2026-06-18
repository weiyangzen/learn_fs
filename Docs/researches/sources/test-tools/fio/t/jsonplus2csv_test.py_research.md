# sources/test-tools/fio/t/jsonplus2csv_test.py

## Purpose
Smoke test for converting fio `json+` latency-bin output to CSV with `fio_jsonplus_clat2csv`, including the converter's validation mode.

## Important APIs, Types, and Functions
`run_fio()` chooses an async engine by platform and runs a three-job fio workload producing `fio-output.json` in `json+` format. `check_output()` runs the converter once normally and once with `--validate`. `parse_args()` and `main()` resolve paths and report pass/fail count.

## Control Flow
The script resolves the fio executable and converter path, runs fio for a short random read/write workload with slat/clat/lat percentiles enabled, then checks that CSV generation and validation both exit zero.

## State and Persistence Behavior
Writes `fio-output.json`, `fio-output.csv`, and the workload target file in the current working directory. No artifact root isolation is provided.

## Dependencies and Integration Points
Depends on fio, the converter under `tools/fio_jsonplus_clat2csv`, Python subprocess support, and an async ioengine (`libaio`, `windowsaio`, or `posixaio`) to produce submission latencies.

## Risks
Current-directory outputs can collide with existing files. It only checks command success, not CSV contents directly. If platform async engine support is unavailable, fio fails before converter behavior is tested.

## Test Signals
The signal is one passing test after fio generation, CSV conversion, and converter self-validation succeed.
