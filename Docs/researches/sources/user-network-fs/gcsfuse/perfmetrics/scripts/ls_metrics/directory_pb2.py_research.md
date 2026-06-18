<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/ls_metrics/directory_pb2.py -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/ls_metrics/directory_pb2.py

## Purpose
Generated Python protobuf bindings for `directory.proto`.

## Important APIs, Types, And Functions
Exports `Directory` and `DESCRIPTOR`, with self-recursive `folders` field metadata.

## Control Flow
Imported by listing benchmark scripts and tests, then populated via `ParseDict` from JSON configs.

## State And Persistence Behavior
No durable state; module registration occurs with the protobuf symbol database at import time.

## Dependencies
Generated for the classic Python protobuf runtime APIs such as descriptors, reflection, and symbol database.

## Integration Points
Must stay in sync with `directory.proto` and with the protobuf runtime pinned by `ls_metrics/requirements.in` and wrapper environment.

## Risks And Edge Cases
Generated-code/runtime version mismatch can raise descriptor errors; the wrapper sets `PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python` to reduce this risk.

## Test Signals
Indirectly covered by `listing_benchmark_test.py` fixture parsing and field traversal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/ls_metrics/directory_pb2.py -->
