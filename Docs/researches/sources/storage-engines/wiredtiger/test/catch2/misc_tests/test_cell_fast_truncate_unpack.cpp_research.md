# sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_cell_fast_truncate_unpack.cpp

## Purpose
Tests packing and unpacking of fast-truncate page-deletion information from address-delete cells, including committed and prepared deletion metadata.

## Important APIs, Types, And Functions
`build_ft_addr_del_cell` manually creates a `WT_CELL_ADDR_DEL` with optional `WT_CELL_PREPARE`, transaction ID, timestamps/prepared ID, and zero-length address cookie. `build_prepared_addr_cell` creates a regular prepared addr cell. `setup_mock_session` initializes mock block-manager operations and base write generation. Tests call `__wt_cell_unpack_addr` and `__wt_cell_pack_addr`.

## Control Flow
Tests unpack hand-built committed and prepared fast-truncate cells, then pack committed and prepared `WT_PAGE_DELETED` structures and unpack them again. A final test verifies a prepare flag on a non-fast-truncate addr cell marks the page-level time aggregate as prepared instead of populating page deletion info.

## State And Persistence Behavior
All cell bytes are in local `WT_CELL` buffers, modeling on-disk address cells. Prepared fast-truncate pack requires connection/table flags `WT_CONN_PRESERVE_PREPARED` and `WT_BTREE_DISAGGREGATED`.

## Dependencies And Integration Points
Depends on `mock_session`, `wt_internal.h`, variable-length integer packing, `WT_PAGE_DELETED`, `WT_TIME_AGGREGATE`, and page header flags like `WT_PAGE_FT_UPDATE`.

## Risks And Edge Cases
Guards against mixing prepared timestamp/prepared ID with commit timestamps, incorrectly marking page aggregate prepare for fast-truncate deletion, and losing `selected_for_write` or committed state on round trip.

## Test Signals
`CHECK` assertions verify transaction IDs, timestamps, prepared IDs, prepare state, committed flag, selected-for-write, and `unpack.ta.prepare`.
