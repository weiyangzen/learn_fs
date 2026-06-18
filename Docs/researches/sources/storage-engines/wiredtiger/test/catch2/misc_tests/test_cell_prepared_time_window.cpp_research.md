# sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_cell_prepared_time_window.cpp

## Purpose
Tests cell validity-window packing/unpacking for prepared time-window metadata, including start-prepared, stop-prepared, both-prepared, regular, and empty windows.

## Important APIs, Types, And Functions
`create_test_time_window` builds `WT_TIME_WINDOW` values with commit/durable timestamps and optional prepared fields. `pack_time_window` calls `__cell_pack_value_validity`. `unpack_time_window` wraps the packed validity bytes inside a mock `WT_CELL_VALUE` and calls `__wt_cell_unpack_kv`. `compare_time_windows` compares all relevant fields.

## Control Flow
Each test creates a mock session, enables `WT_CONN_PRESERVE_PREPARED`, sets up block-manager operations and `base_write_gen`, builds a time window, packs it, unpacks it, and compares. The empty test checks compact packed size.

## State And Persistence Behavior
The file models on-disk cell bytes in memory. It does not write to disk but depends on page header write generation to avoid obsolete cleanup paths during unpack.

## Dependencies And Integration Points
Depends on Catch2, `mock_session`, `wt_internal.h`, `WT_TIME_WINDOW`, cell packing/unpacking internals, and preserve-prepared connection behavior.

## Risks And Edge Cases
Risks include losing prepared IDs/timestamps during packing, mishandling same-transaction start/stop prepared windows, and breaking regular non-prepared time windows while adding prepared metadata.

## Test Signals
Packed empty window size must be one byte; all nonempty scenarios must unpack to field-equivalent `WT_TIME_WINDOW` structures.
