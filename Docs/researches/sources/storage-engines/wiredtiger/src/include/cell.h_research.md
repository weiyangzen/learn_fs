<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/cell.h -->
# sources/storage-engines/wiredtiger/src/include/cell.h

## Purpose
Defines WiredTiger's variable-length on-page cell format and unpacked cell structures. Cells encode row/column keys, values, overflow references, deleted placeholders, internal-page addresses, timestamp/transaction visibility windows, fast-truncate metadata, dictionary copies, and delta-page merge state.

## Important APIs, Types, and Functions
Descriptor-bit macros define short key/value encodings, associated 64-bit value presence, secondary descriptor presence, time-window flags, raw cell types, cell type masking, and size adjustment for non-short cells.

`WT_CELL` is the packed on-page header buffer, sized pessimistically for all optional metadata.

`WT_CELL_COMMON_FIELDS` defines the common unpack fields: original cell pointer, RLE/recno `v`, data pointer and size, cell length, prefix byte, raw/type fields, and flags.

`WT_CELL_UNPACK_ADDR` adds a `WT_TIME_AGGREGATE` and `WT_PAGE_DELETED` for internal address cells and fast truncation. `WT_CELL_UNPACK_KV` adds a `WT_TIME_WINDOW` for key/value cells.

Delta structures include `WT_CELL_UNPACK_DELTA_INT`, `WT_CELL_UNPACK_DELTA_LEAF_KV`, `WT_CELL_KV`, `WTI_DELTA_INT_MERGE_STATE`, and `WTI_BASE_INT_MERGE_STATE`.

## Control Flow
The packed format starts with a descriptor byte. Short cells store type and length entirely in that byte. Non-short cells may include a prefix byte, a second descriptor byte with timestamp/transaction flags, an associated packed 64-bit value such as RLE or recno, fast-delete fields, a packed data length, and then data bytes or an address cookie. Unpack structures normalize those variants so higher-level code can operate on typed fields.

## State and Persistence Behavior
Unlike most inline headers, this file defines a persistent on-disk format. The descriptor values, field order, delta encoding assumptions, and size adjustment are compatibility-sensitive. `WT_CELL_ADDR_DEL` and `WT_CELL_ADDR_DEL_VISIBLE_ALL` preserve fast-truncate state, while time windows and aggregates preserve MVCC visibility across restart.

## Dependencies and Integration Points
The format depends on WiredTiger timestamp, transaction, page delete, page header, item, and block metadata types. It integrates with reconciliation, page read, overflow management, row/column accessors, truncate, history store visibility, disaggregated delta leaf/internal pages, and verification.

## Risks and Edge Cases
Changing descriptor bits or field ordering is an on-disk compatibility change. `WT_CELL_VALUE_COPY` means an unpacked value may refer to an earlier cell while keeping the current cell's visibility/RLE metadata. Prepared transaction metadata reuses timestamp flag slots in specialized ways when preserving prepared IDs. Fast-truncate address cells carry page-delete metadata only when the page image advertises `WT_PAGE_FT_UPDATE`.

## Test Signals
Coverage should include page image format compatibility, verify on malformed cells, timestamped and non-timestamped visibility windows, prepared updates with and without preserve-prepared, overflow cells, dictionary values, fast truncate, row prefix compression, column RLE, and delta page merge tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/cell.h -->
