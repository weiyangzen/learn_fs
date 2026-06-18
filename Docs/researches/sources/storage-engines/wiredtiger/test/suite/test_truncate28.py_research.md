# sources/storage-engines/wiredtiger/test/suite/test_truncate28.py

## Purpose
`test_truncate28.py` tests that fast truncate cannot be committed with an invalid timestamp ordering relative to a prepared update, and that the expected timestamp usage error is raised.

## Important APIs, Types, and Functions
The class defines `evict_cursor` and `test_truncate28`. It uses diagnostic/standalone build guards, timestamped inserts, prepared transactions (`prepare_transaction`, `timestamp_transaction` for commit and durable timestamps), stable timestamp movement, eviction, truncate, and `assertRaisesWithMessage`.

## Control Flow
The test skips unsupported builds, populates timestamped rows, creates a prepared update at chosen prepare/commit/durable timestamps, stabilizes and checkpoints, evicts data, then starts a truncate from key 1 and attempts to commit it at an earlier timestamp that violates rules.

## State and Persistence Behavior
The table carries prepared update metadata and timestamped fast-delete candidates. No successful persistence of the invalid truncate is expected.

## Dependencies and Integration Points
Depends on WiredTiger build-mode introspection, prepared transaction validation, timestamps, and error pattern reporting.

## Risks and Edge Cases
This protects against accepting a truncate timestamp that conflicts with prepared update visibility. Build skips mean coverage applies only to non-diagnostic standalone builds.

## Test Signals
The truncate commit must raise `WiredTigerError` with `/unexpected timestamp usage/`.
