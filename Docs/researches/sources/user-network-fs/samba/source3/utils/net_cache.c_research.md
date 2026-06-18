# sources/user-network-fs/samba/source3/utils/net_cache.c

Purpose: implements `net cache`, a local wrapper around Samba `gencache` and samlogon cache data for inspection, testing, addition, deletion, and flushing.

Important APIs/types/functions: `net_cache()` dispatches `add`, `del`, `get`, `search`, `list`, `flush`, and nested `samlogon`. Helpers include `print_cache_entry()`, `delete_cache_entry()`, `parse_timeout()`, and samlogon `list/show/ndrdump/delete` functions.

Control flow: basic commands parse arguments and call `gencache_set()`, `gencache_del()`, `gencache_get_data_blob()`, or iterator APIs. `print_cache_entry()` formats timeouts, decodes known `NAME2SID/` and `SID2NAME/` string-vector values, prints printable blobs, and labels other values as binary. Samlogon paths parse SIDs, retrieve `netr_SamInfo3`, derive SID arrays, or NDR-print records.

State and persistence: mutates local generic cache entries and samlogon cache entries. `flush` deletes every matching gencache key; `samlogon delete` clears one cached user. List/search/show are read-only.

Dependencies/integration: uses `libsmb/samlogon_cache.h`, Netlogon NDR types, SID helpers, `strv`, `lib/gencache.h`, and `net_run_function()`.

Risks: `parse_timeout()` relies on `atoi()` and weakly validates empty/nonnumeric strings. `flush` is intentionally broad and destructive. Binary values are not fully decoded. Samlogon output assumes valid cache/NDR layout.

Test signals: add/get/del/list/search with relative and expired timeouts; printable/binary formatting; `NAME2SID`/`SID2NAME` decoding; flush on isolated cache; samlogon list/show/ndrdump/delete with valid/invalid SIDs.
