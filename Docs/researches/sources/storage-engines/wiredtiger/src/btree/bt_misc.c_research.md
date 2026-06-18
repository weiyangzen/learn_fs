# sources/storage-engines/wiredtiger/src/btree/bt_misc.c

Purpose: small B-tree utility formatting helpers used by diagnostics, verbose output, and debugger-visible code. It converts addresses, cell types, keys, and page types into stable printable strings.

Important APIs/types/functions: `__wt_addr_string` formats a block-manager address or returns sentinel strings for no-address/error cases. `__wti_cell_type_string` maps `WT_CELL_*` raw types to readable names. `__wt_key_string` formats keys according to a WiredTiger key format, with diagnostic raw-dump support. `__wt_page_type_string` maps `WT_PAGE_*` constants and is exported with default visibility.

Control flow: address formatting obtains `S2BT_SAFE(session)`, delegates to `btree->bm->addr_string` when possible, and falls back to `WT_NO_ADDR_STRING` or `WT_ERR_STRING`. Key formatting special-cases string format `S` by building a null-terminated temporary if needed, then calls printable-format helpers; diagnostic `session->dump_raw` bypasses format rendering. Cell/page type helpers are direct switches with `"unknown"` fallback.

State and persistence behavior: no persistent state is changed. The functions write into caller-provided `WT_ITEM` buffers or return string literals. `__wt_key_string` may allocate a temporary `WT_ITEM` internally and frees it before returning; callers must provide a persistent output buffer for the returned string data.

Dependencies and integration points: used heavily by `bt_debug.c`, verification/dump code, logging, error messages, and any code that needs to display B-tree page/cell/address identity. It depends on block-manager address formatting, struct-format printable conversion, scratch buffer management, and diagnostic raw-dump session state.

Risks: callers must pass valid buffers; `__wt_addr_string` asserts this. `__wt_key_string` assumes nonzero size when checking the final byte for `S` string keys, so callers should not pass malformed zero-length string keys. Type string switches must stay updated when new page or cell types are introduced to avoid vague diagnostics.

Test signals: formatting null/empty addresses, missing block manager fallbacks, valid block-manager address strings, all known cell/page types, unknown type fallback, string keys with and without trailing NUL, raw dump mode, and formatted binary/structured keys.
