# sources/test-tools/fio/t/nvmept_trim.py

Purpose: destructive NVMe passthrough dataset-management trim coverage for `io_uring_cmd`, including legacy trim workloads, multi-range trims, rate/accounting checks, invalid configurations, and data-pattern verification around deallocated ranges.

Important APIs and types: `TrimTest` extends `FioJobCmdTest` and centralizes fio argument construction and JSON data-direction validation. `RangeTrimTest` adds `get_bs()` for exact or average block-size calculation from `bs`, `bssplit`, or `bsrange`, and overrides `check_result()` to verify bandwidth, IOPS, total IO counts, and rate expectations for multi-range trim requests.

Control flow: `main()` parses fio path and destructive `--dut`, creates artifacts, injects filename, and calls `run_fio_tests()`. The test list first covers plain trim/randtrim/trimwrite/randtrimwrite and iodepth cases, then multi-range trim sizes and variable block sizes, then expected-failure invalid combinations, then a multi-step data-integrity scenario: write a pattern, verify it, trim half the namespace, confirm the trimmed half no longer returns the old pattern, and verify the untrimmed half.

State and persistence: the target namespace is modified by writes and trims. fiotestlib persists JSON and stdout/stderr artifacts. The script does not restore data, and multi-step tests depend on earlier steps preserving device state for later checks.

Dependencies and integration points: depends on Python, fio, fiotestlib, `SUCCESS_NONZERO`, Linux NVMe character device passthrough support, and a target device safe for destructive testing. It is included in `run-fio-tests.py` as an NVMe character-device executable test.

Risks and test signals: accounting checks use averages for `bssplit` and `bsrange`, so they tolerate fuzz rather than proving every range offset. There is a repeated `verify` option in the option allowlist and a likely typo `fixedbuffs` in one test option, useful for regression awareness. Success signals are fio return code, JSON direction counters, iodepth bucket checks, calculated byte totals within 5 percent, IO count match within tolerance, rate within 5 percent, and expected non-zero exits for unsupported range trimwrite or too many ranges.
