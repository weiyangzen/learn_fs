# sources/test-tools/fio/t/strided.py

Purpose: regression tests for `zonemode=strided`. It verifies that random reads stay inside the current zone/range and, when random mapping or LFSR makes uniqueness meaningful, that each block in a range is touched exactly once before wrap.

Important APIs and types: `StridedTest` extends `FioJobCmdTest`. `setup()` builds fio commands with `--zonemode=strided`, `--log_offset=1`, `--write_iops_log`, and zone size/range/block options. `check_result()` parses the IOPS log lines supplied by fiotestlib and validates offsets.

Control flow: `main()` creates artifacts, resolves fio, optionally stats a user-supplied target file/device, populates each test with either a real filename/filesize or null-engine filesize, then calls `run_fio_tests()`. The matrix covers randommap-enabled, LFSR, and `norandommap` cases with equal, larger, and smaller `zonesize` versus `zonerange`, plus optional offsets.

State and persistence: with no `--dut`, null engine avoids storage changes. With a supplied target file/device, the script performs random reads only. It writes logs and output artifacts under the artifact root.

Dependencies and integration points: depends on Python, fio, fiotestlib, and optionally a target file/device. It is included in `run-fio-tests.py` as executable test 1006.

Risks and test signals: some `io_size` constants appear to use `256*1024*204`, likely intentional historical coverage or a typo that reduces size below the associated `size`. `check_result()` prints and returns on failures without explicitly setting `self.passed = False` in several branches, so some detected violations may not fail the test. Intended success signals are offsets within zone bounds and complete unique coverage where applicable.
