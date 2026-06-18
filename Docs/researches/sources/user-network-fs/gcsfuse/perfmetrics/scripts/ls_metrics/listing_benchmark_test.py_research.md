<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/ls_metrics/listing_benchmark_test.py -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/ls_metrics/listing_benchmark_test.py

## Purpose
Regression tests for listing benchmark pure logic and mocked subprocess interactions.

## Important APIs, Types, And Functions
Defines several `Directory` protobuf fixtures through `ParseDict`, expected metric rows, and `unittest` cases around listing benchmark helpers.

## Control Flow
The suite validates counting recursion, statistical parse output, worksheet export calls, timing calculations, recursive directory creation, GCS directory comparison, and the global `RUN_1M_TEST` filter.

## State And Persistence Behavior
It does not persist state; all GCS listing and file generation effects are mocked. Global patching of `RUN_1M_TEST` demonstrates expected inclusion/exclusion of the 1M-file test.

## Dependencies
Depends on `directory_pb2`, `google.protobuf`, `mock`, and the local `listing_benchmark` module.

## Integration Points
Serves as executable documentation for config and proto contracts consumed by the listing benchmark.

## Risks And Edge Cases
The suite does not execute the main CLI, real bucket deletion, real `gcsfuse`, BigQuery upload, or cleanup paths, so deployment failures remain possible.

## Test Signals
Coverage is broad for helper functions, especially tree comparison edge cases and recursive file generation call ordering.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/ls_metrics/listing_benchmark_test.py -->
