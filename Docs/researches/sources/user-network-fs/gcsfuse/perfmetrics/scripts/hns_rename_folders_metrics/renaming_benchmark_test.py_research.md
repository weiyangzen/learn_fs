<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/hns_rename_folders_metrics/renaming_benchmark_test.py -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/hns_rename_folders_metrics/renaming_benchmark_test.py

## Purpose
Unit tests for the rename benchmark helper functions and top-level orchestration branches.

## Important APIs, Types, And Functions
Uses `unittest`, `mock.patch`, `call`, and `mock_open` to isolate subprocess, time, mount, JSON, Google Sheets, and VM metric behavior.

## Control Flow
Tests construct small folder-config dictionaries, patch external effects, invoke private helpers directly, and assert timing lists, time intervals, subprocess calls, generated export rows, and upload calls.

## State And Persistence Behavior
No durable state is intended; all filesystem, sleep, subprocess, and network-facing work is mocked. One duplicate `test_get_upload_value_for_vm_metrics` method shadows the earlier identical definition.

## Dependencies
Depends on the local `renaming_benchmark` module and the legacy `mock` package as well as stdlib `unittest`.

## Integration Points
Documents the expected contract for `run_rename_benchmark.sh` and for worksheet upload rows consumed downstream.

## Risks And Edge Cases
The tests assert implementation details but do not run real GCSFuse, Cloud Monitoring, or credential flows. Some fixture shapes differ from production config shape, so mount-flag tests can miss nested-folder assumptions.

## Test Signals
This file is itself the signal; it covers most pure functions but leaves CLI parsing, dependency checks, and real subprocess failure behavior thin.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/hns_rename_folders_metrics/renaming_benchmark_test.py -->
