# sources/user-network-fs/samba/source3/lib/eventlog/eventlog.c

Purpose: manages source3 eventlog TDB files and converts records between internal TDB form and Windows EVENTLOG/EVT structures.

Important APIs/types/functions: `elog_init_tdb()`, `elog_tdbname()`, `elog_tdb_size()`, `prune_eventlog()`, `elog_open_tdb()`, `elog_close_tdb()`, `parse_logentry()`, `fixup_eventlog_record_tdb()`, pull/push helpers, entry conversion helpers, and `evlog_convert_tdb_to_evt()`.

Control flow: eventlogs live under `state_path("eventlog")`. Open reuses or initializes a TDB, validates version, and tracks refcounts. Push locks `EVT_NEXT_RECORD`, assigns a number, NDR-encodes and stores the record, then increments metadata. Pull fetches and NDR-decodes. Export iterates records and builds an EVT blob.

State/persistence behavior: TDB metadata stores oldest entry, next record, max size, retention, and version. Records are NDR blobs keyed by int32 record number. Pruning deletes old records and advances oldest-entry metadata.

Dependencies/integration: depends on TDB, state paths, DLIST, NDR eventlog structures, SID/string conversion, and RPC eventlog services.

Risks/test signals: risks include record-number corruption, retention mis-pruning, SID/string padding errors, and refcount misuse. Tests should cover open/close, version reset, push/pull round trips, pruning, parser input, and EVT export.
