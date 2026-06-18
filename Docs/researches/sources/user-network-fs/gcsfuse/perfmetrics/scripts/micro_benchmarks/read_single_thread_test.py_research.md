<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/micro_benchmarks/read_single_thread_test.py -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/micro_benchmarks/read_single_thread_test.py

## Purpose
Unit tests for read microbenchmark file creation and read loops.

## Important APIs, Types, And Functions
Mocks builtins `open`, `os.path`, `subprocess.run`, `google.cloud.storage.Client`, and GCS blob methods.

## Control Flow
Tests validate expected path naming, successful byte totals, RuntimeError wrapping on IO failures, and object upload decisions for missing, small, and correctly sized blobs.

## State And Persistence Behavior
All filesystem and GCS effects are mocked, including cleanup through `os.remove`.

## Dependencies
Depends on local `read_single_thread` and stdlib unittest mocks.

## Integration Points
Captures the contract used by the periodic microbenchmark wrapper.

## Risks And Edge Cases
Does not exercise CLI `main`, mount failures, BigQuery logging, or memory use from real large reads.

## Test Signals
Good focused coverage for helper branches; integration behavior remains untested.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/micro_benchmarks/read_single_thread_test.py -->
