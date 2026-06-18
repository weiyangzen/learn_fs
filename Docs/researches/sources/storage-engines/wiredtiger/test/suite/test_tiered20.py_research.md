# sources/storage-engines/wiredtiger/test/suite/test_tiered20.py

## Purpose
`test_tiered20.py` checks that tiered storage never overwrites existing shared objects and detects conflicts across local databases sharing a bucket.

## Important APIs, Types, and Functions
The file defines `wt_boolean`, `test_tiered20`, `additional_conn_config`, `create_flush_drop`, and `file_contains`. Tiered scenarios use short retention/interval settings and `debug_mode=(tiered_flush_error_continue=true)` so flush errors can be asserted instead of crashing the test process.

## Control Flow
The test first repeatedly creates, flushes, and drops a table with `remove_shared=true`. It then creates and drops another table without removing shared objects and verifies recreating the same URI detects `EEXIST`. Next it creates a second WT home sharing the directory-store bucket via symlink, creates the same URI in both homes, writes different payloads, checkpoints both, flushes from the first home successfully, and expects the second flush to fail with `EEXIST`. It verifies the original bucket file still contains the first payload, waits for local removal, reopens, and reads through the cloud copy.

## State and Persistence Behavior
It exercises shared object immutability, bucket collision detection, local retention cleanup, and data recovery after local object removal.

## Dependencies and Integration Points
It integrates with tiered drop, flush error handling, directory-store no-overwrite policy, multi-home connections, symlinked bucket directories, and binary file inspection.

## Risks and Test Signals
Risks include clobbering shared objects or missing collisions after local metadata is removed. Signals are expected `EEXIST`, unchanged file contents, and successful cloud readback.
