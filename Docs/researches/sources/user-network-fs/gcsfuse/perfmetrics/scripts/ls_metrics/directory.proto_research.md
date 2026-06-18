<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/ls_metrics/directory.proto -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/ls_metrics/directory.proto

## Purpose
Defines the recursive directory schema used by listing benchmarks and config JSON parsing.

## Important APIs, Types, And Functions
Package `perfmetrics` with message `Directory`: `name`, `num_files`, `file_name_prefix`, `file_size`, `num_folders`, and repeated child `folders`.

## Control Flow
JSON configs are parsed into this type with `ParseDict`; recursive benchmark helpers traverse `folders`, use file fields to create workloads, and validate actual bucket listings against the declared counts.

## State And Persistence Behavior
No runtime state; this is the source schema for generated Python code.

## Dependencies
Requires proto3 tooling and generated `directory_pb2.py` for Python consumers.

## Integration Points
Used by `listing_benchmark.py`, its tests, and `config*.json` files.

## Risks And Edge Cases
No validation constraints encode file-size units or count consistency; callers must treat zero defaults carefully.

## Test Signals
Exercised indirectly by listing benchmark tests that parse fixture dictionaries into `Directory` messages.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/ls_metrics/directory.proto -->
