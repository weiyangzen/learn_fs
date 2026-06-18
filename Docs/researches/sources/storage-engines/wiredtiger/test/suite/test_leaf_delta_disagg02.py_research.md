# sources/storage-engines/wiredtiger/test/suite/test_leaf_delta_disagg02.py

## Purpose
Tests the `page_delta.delete_pct` threshold that forces reconciliation to write a full leaf page instead of a delta when too many disk-image keys are removed.

## APIs, Types, And Functions
Defines `test_leaf_delta_disagg02` under disaggregated storage scenarios. It uses `page_delta=(delta_pct=1000,delete_pct=50)`, data-source stats `rec_page_delta_leaf` and `rec_page_delta_rejected_delete_threshold`, timestamped per-key transactions, and read timestamp verification.

## Control Flow, State, And Persistence
`populate` creates ten deterministic keys on one leaf page and checkpoints at a base timestamp. One test deletes seven keys, advances oldest/stable timestamps, checkpoints, and expects full-page output with delete-threshold rejection. The other deletes three keys and updates four, then expects a delta. Both verify present/absent keys before and after reopening the disaggregated connection.

## Dependencies, Integration, Risks, And Test Signals
Depends on small page layout, deterministic key widths, disaggregated leaf-page delta support, and timestamp visibility. Risks are off-by-one threshold behavior, writing tombstone-heavy deltas when full pages are required, or losing data across restart. Signals are stats counters plus read-timestamp searches after restart.
