# sources/storage-engines/wiredtiger/test/csuite/wt3184_dup_index_collator/main.c

## Purpose
WT-3184 checks that duplicating an index cursor with a custom collator preserves enough key/value state to avoid truncated-key compare failures and returns the expected indexed value.

## Important APIs, Types, and Functions
- Defines `WT_COLLATOR index_coll` using `index_compare`.
- Uses `wiredtiger_struct_unpack(session, ..., "uu", ...)` to unpack index and primary key parts from packed index keys.
- `item_to_int`, `compare_int_items`, and `print_int_item` interpret `WT_ITEM` payloads as 32-bit integers while avoiding misaligned loads.
- Uses `session->open_cursor(session, NULL, cursor, NULL, &cursor1)` to duplicate the positioned cursor.

## Control Flow
The test opens a clean home, registers `index_coll`, creates `table:main` with unpacked item key/value formats, and creates `index:main:index` on column `v` with the custom collator. It inserts one record with key `13` and value `17`, searches the index by value, duplicates the index cursor, and asserts both original and duplicate return value `17`.

## State and Persistence Behavior
The table and secondary index are persistent within the test home, though no reopen is performed. Cursor state after `search` is the critical state under test; duplication must preserve the positioned index cursor.

## Dependencies and Integration Points
The test depends on custom collator registration and WiredTiger's packed struct format for index keys. It integrates with the C API cursor duplication path and index cursor value retrieval.

## Risks and Test Signals
Failures point to collator comparison receiving malformed/truncated packed keys, cursor duplication losing state, or index cursor value mismatch. The test only inserts one record, so it is surgical rather than broad coverage of duplicate-key ordering.
