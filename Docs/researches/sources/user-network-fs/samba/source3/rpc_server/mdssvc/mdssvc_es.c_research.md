# sources/user-network-fs/samba/source3/rpc_server/mdssvc/mdssvc_es.c

Purpose: implements the Elasticsearch-backed mdssvc search backend. It translates Spotlight query syntax to Elasticsearch query-string syntax, maintains an HTTP(S) connection to an ES server, pages results, and feeds matching `path.real` values back into the common mdssvc result path.

Important APIs and functions: `mdssvc_es_init()` loads JSON mappings from `elasticsearch:mappings` or the Samba datadir default and records `elasticsearch:default_fields`. `mds_es_connect()` creates per-bind `struct mds_es_ctx` and starts async HTTP connection setup. `mds_es_search()` maps the Spotlight query with `map_spotlight_to_es_query()`, allocates `struct sl_es_search`, sets page size and max results, links it to the queue, and triggers dispatch. `mds_es_search_send()` builds a POST to `/<index>/_search`, using `MDSSVC_ELASTIC_QUERY_TEMPLATE` with `_source` limited to `path.real`. `mds_es_search_http_read_done()` parses JSON responses and calls `mds_add_result()` for each hit.

Control flow: backend init is process-level; `connect` is per mdssvc bind/share and asynchronously connects to ES using loadparm `elasticsearch:address`, `port`, `use tls`, and credentials. Searches are queued in `mds_es_ctx->searches`, with only the list head pending on the HTTP channel. Completion updates the common `sl_query` state: no total or max reached becomes `DONE`, a full page in the client queue becomes `FULL`, otherwise the search is requeued for another page. `search_cont()` re-adds the search when the client drains results.

State and persistence: `mdssvc_es_ctx` persists mappings/default fields for the process. `mds_es_ctx` stores the HTTP connection and active queue per bind. `sl_es_search` stores paging counters, max result cap, and translated ES query. ES itself is the persistent index; Samba stores only transient cursors.

Dependencies: tevent, Samba HTTP client, TLS parameter setup, credentials, Jansson, loadparm, generated ES parser, mdssvc core, and the common VFS/access path in `mds_add_result()`.

Risks: the JSON query is assembled with `talloc_asprintf()`, so correctness relies on mapper escaping. HTTP reconnect marks the query error and reconnects the shared channel. A pending search survives `sl_query` destruction by clearing `slq`; lifetime rules are subtle. Response size is bounded by `SL_PAGESIZE * 8192`, which may truncate unusually large hits. `mdssvc_es_shutdown()` does not explicitly decref mappings, relying on talloc/process cleanup, so allocator ownership deserves attention.

Test signals: `test_mdsparser_es.c` verifies query mapping. Integration tests should cover ES 6/7 total-hit formats, paging, max result caps, TLS/non-TLS connection, missing `path.real`, non-200 responses, reconnect paths, and client-close while HTTP is pending.
