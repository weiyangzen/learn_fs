# sources/storage-engines/rocksdb/monitoring/iostats_context_test.cc

Purpose: Unit test for `IOStatsContext::ToString` zero filtering behavior.

Important APIs/types/functions: Test `IOStatsContextTest.ToString` calls `get_iostats_context()->Reset()`, sets `bytes_read`, then compares formatted strings with and without `exclude_zero_counters`.

Control flow: The test asserts the default string contains both zero-valued counters and the non-zero `12345` value. It then asserts the zero-excluding string omits `"= 0"` while still containing the non-zero value.

State/dependencies: Uses the thread-local IO stats context and RocksDB test harness. The main function installs stack traces and runs Google Test.

Risks/test signals: Coverage is narrow: it does not validate every counter, timer macro, disabled build, or temperature sub-counters. It gives a direct regression signal for formatting and zero filtering.
