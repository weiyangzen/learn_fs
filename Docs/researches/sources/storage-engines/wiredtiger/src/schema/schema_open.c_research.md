# sources/storage-engines/wiredtiger/src/schema/schema_open.c

Purpose: opens and validates in-memory schema structures for tables, column groups, indexes, layered tables, page logs, and storage sources, and rejects removed fixed-length column-store formats.

Important APIs and functions: `__wti_schema_open_colgroups`, `__wt_schema_open_index`, `__wt_schema_open_indices`, `__wt_schema_open_table`, `__wt_schema_open_layered`, `__wt_schema_open_page_log`, `__wt_schema_open_storage_source`, `__wt_schema_get_colgroup`, `__wti_schema_get_index`, `__wt_schema_tiered_shared_colgroup_name`, and `__wt_schema_unsupported_format`. Internal helpers include `__schema_colgroup_name`, `__open_index`, `__schema_open_index`, `__schema_open_table`, `__schema_open_layered`, and `__schema_open_layered_ingest`.

Control flow: table open parses key/value formats, column config, simplicity, column-group list, shared-tiered marker, allocates column-group slots, and opens column groups. Column-group open builds metadata URIs, tolerates missing metadata for incomplete tables, loads source and column config, checks complex-table coverage, and builds the projection plan. Index open scans metadata keys under `index:<table>:` in sorted order, synchronizes the table's in-memory index array with metadata, loads source/collator/formats, derives key and value projection plans, and sets completion flags after a full pass. Layered open validates disaggregated storage, rejects custom collators, loads key/value/ingest/stable URIs, opens the ingest table to record its btree id, and registers it with the layered manager.

State and persistence behavior: this file builds in-memory schema caches and manager registrations. It does not write metadata. It may allocate and free table/index/column-group structures, set completion flags, store projection strings, set immutable index flags, and add layered ingest ids to the manager.

Dependencies and integration points: depends on metadata cursors, config parsing, table write locks, read-uncommitted schema reads, collator configuration, format/planning helpers from `schema_plan.c`, layered manager APIs, extension queues for page logs/storage sources, and dhandle APIs for constituent opens.

Risks: index-array synchronization uses sorted metadata traversal and memmove; ordering mistakes can leak or stale indexes. Opening indexes before column groups are complete intentionally validates without caching. Layered shutdown needs the ingest btree id even while handles are being swept. The FLCS unsupported-format check must run during create/open upgrades to prevent use of removed formats.

Test signals: open simple and complex tables, incomplete tables, tiered shared column groups, index creation/open with collators and hidden primary-key columns, dropped-index synchronization, page-log/storage-source lookup failures, layered table open in disaggregated and non-disaggregated connections, and FLCS create/open rejection messages.
