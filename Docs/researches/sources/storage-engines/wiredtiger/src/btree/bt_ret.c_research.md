# sources/storage-engines/wiredtiger/src/btree/bt_ret.c

## Purpose

`bt_ret.c` contains helpers that expose the currently positioned btree cursor key, value, and time-window metadata through the interface cursor. It handles row-store keys, variable column-store record numbers, on-page values, visible update values, and overflow-removed restart races. The complete 263-line source was read.

## Important APIs, Types, and Functions

`__wt_key_return` publishes a cursor key and delegates to `__key_return`. `__wt_value_return` publishes a visible standard update value. `__wt_value_return_buf` references original on-page value bytes and optionally returns a `WT_TIME_WINDOW`. `__wt_read_cell_time_window` extracts current on-page cell time-window metadata. `__wti_read_row_time_window`, `__read_col_time_window`, and `__read_page_cell_data_ref_kv` are support helpers.

## Control Flow

For row leaves, `__key_return` returns insert-list keys directly, swaps `cbt->row_key` with `cbt->tmp` for exact search matches, or materializes the slot key from the page. For variable column-store pages it sets `cursor->recno`. `__wt_key_return` avoids rebuilding a key if an internal key is already present.

`__wt_value_return_buf` uses the encoded simple-value shortcut when possible, otherwise unpacks row or column cells and references the value. `__read_page_cell_data_ref_kv` returns `WT_RESTART` if it sees a removed overflow value. `__wt_value_return` assumes the caller already resolved visibility and deletion and points the interface value at the update buffer.

## State and Persistence Behavior

This file writes no persistent state. It mutates cursor key/value/recno fields and internal/external cursor flags. The exact-match key path swaps temporary buffers to preserve returned-key lifetime across subsequent searches. Value and key returns often reference internal page or update memory, so validity is tied to cursor/page lifetime.

## Dependencies and Integration Points

It depends on row/column page layouts, insert lists, cell unpacking, overflow handling, update visibility conventions, time-window macros, and cursor standard flags. Callers are search, traversal, random cursor, and update paths that need to expose data through `WT_CURSOR`.

## Risks and Edge Cases

The main risks are buffer lifetime and caller contract violations. Returning `cbt->tmp` directly would corrupt keys after later searches, so the swap is required. `__wt_value_return` must only receive visible full standard updates. Column-store time-window reads must reject insert positions that do not match the on-page slot. Removed overflow cells must trigger retry rather than exposing freed data.

## Test Signals

Cover insert-list keys, exact-search key buffer swapping, row slot key materialization, column recno return, simple encoded values, overflow values, overflow-removed `WT_RESTART`, update-chain value return, and time-window extraction for row and variable-column pages.
