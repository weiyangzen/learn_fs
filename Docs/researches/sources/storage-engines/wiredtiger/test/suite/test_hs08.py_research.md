# sources/storage-engines/wiredtiger/test/suite/test_hs08.py

## Purpose

Verifies modify insertion into the history store, including when modifies are preserved, reconstructed, or squashed during checkpoint.

## Important APIs, Types, and Functions

Defines `test_hs08`, `get_stat`, and `test_modify_insert_to_hs`; uses `wiredtiger.Modify`, `cache_write_hs`, and `cache_hs_write_squash`.

## Control Flow

A single key starts with a 1000-byte value, then receives several timestamped append/replace modifies separated by checkpoints. The test reads at timestamps 3, 4, 5, 7, and 8, then applies multiple modifies in the same transaction and across transactions to verify squash accounting under same and different timestamps.

## State and Persistence Behavior

State is a focused single-key HS chain containing full updates, reverse modifies, and squashed modify records. Checkpoints trigger HS writes and stat updates.

## Dependencies and Integration Points

Depends on `wiredtiger.Modify`, all statistics, scenario key formats, timestamped transactions, and checkpoint `use_timestamp=true`.

## Risks and Maintenance Signals

Squash stat assertions are exact for some phases and monotonic for HS writes; internal squash policy changes may require updating counts. Single-key coverage is precise but narrow.

## Test Signals

Signals are exact values at historical timestamps, increasing HS write stats, and expected squash counts for same-timestamp modifies.
