# sources/storage-engines/wiredtiger/src/cursor/cur_dump.c

## Purpose
`cur_dump.c` implements the wrapper cursor used when a WiredTiger cursor is opened with dump formatting. It does not own storage access itself; it sits in front of a child cursor and converts keys and values between raw WiredTiger binary formats and printable dump encodings. It supports normal escaped-hex dump output, hex-only output, pretty printable output, JSON dump output, and raw mode variants.

## Important APIs, Types, and Functions
The central type is `WT_CURSOR_DUMP`, whose public `WT_CURSOR` interface is initialized by `__wti_curdump_create`. The wrapper stores a `child` cursor and reuses the child URI, key format, and value format. `__raw_to_dump` and `__dump_to_raw` are the binary/string conversion helpers, selecting `__wt_raw_to_hex`, `__wt_raw_to_esc_hex`, `__wt_hex_to_raw`, or `__wt_esc_hex_to_raw` based on `WT_CURSTD_DUMP_HEX`.

`__curdump_get_key` and `__curdump_get_value` are the core read paths. They either unpack JSON using `__wt_json_alloc_unpack`, format record-number keys as decimal strings, pretty-print with `__wt_buf_set_printable_format`, or convert raw buffers to dump strings. `__curdump_set_keyv` and `__curdump_set_valuev` reverse the process for write operations, including JSON input conversion through `__wt_json_to_item` and record-number parsing through `str2recno`. `WT_CURDUMP_PASS` forwards `next`, `prev`, `reset`, `search`, `insert`, `update`, and `remove` directly to the child cursor; `bound` and `search_near` are small explicit pass-throughs.

## Control Flow
Cursor creation copies dump-related flags from the child (`WT_CURSTD_DUMP_HEX`, `WT_CURSTD_DUMP_JSON`, `WT_CURSTD_DUMP_PRETTY`, and `WT_CURSTD_DUMP_PRINT`), optionally allocates a shared `WT_JSON` object, and calls `__wt_cursor_init`. Reads call the child first, then translate into the public dump cursor buffers before returning either a `const char *` or `WT_ITEM *` depending on raw mode. Writes read application arguments, translate them into `cursor->key` or `cursor->value`, then call `child->set_key` or `child->set_value`.

Record-number stores get special handling: non-raw dump keys are decimal strings, while JSON keys are unpacked from the JSON item and decoded as packed unsigned integers. Errors in `set_keyv` and `set_valuev` are saved in `cursor->saved_err` and clear the corresponding key/value-set flags.

## State and Persistence Behavior
This file is a presentation layer. It does not persist data directly and does not change transaction semantics beyond invoking the child cursor. It owns transient conversion buffers in the public cursor and a JSON-private object when JSON mode is active. Closing a dump cursor closes the child cursor, clears `internal_uri` because the URI memory is shared with the child, closes JSON state, and frees the wrapper cursor.

## Dependencies and Integration Points
The implementation depends on standard cursor API macros, raw/escaped hex helpers, JSON helpers, format-aware printable-buffer helpers, and the child cursor's full operation table. It is created from the standard cursor open path when a file/table/index cursor is opened with dump configuration. Index and table cursor code intentionally disables nested dump behavior for their internal child cursors so only the top-level user cursor becomes a dump wrapper.

## Risks and Edge Cases
The main risks are format conversion mismatches and state flag drift between the wrapper and child. Record-number parsing rejects signs, prefixes, and trailing text, but it still relies on string input matching decimal recno expectations. Pretty-print mode ignores formatting failures with `WT_IGNORE_RET`, so it may fall back less visibly than hard conversion paths. JSON mode shares `json_private` between wrapper and child, making close ordering important. Because many operations are passed straight through, child cursor errors and positions are authoritative, while wrapper buffers only reflect the latest successful get/set path.

## Test Signals
Relevant coverage appears in dump and salvage usage, plus `test_cursor_bound16.py`, which exercises bounded cursor behavior on dump cursors. Broader smoke coverage comes from backup/verify/dump workflows and format failure-dump paths. Useful additional signals would include JSON dump round trips, record-number set/get failures, raw-mode `WT_ITEM` lifetime checks, and child-error propagation through forwarded operations.
