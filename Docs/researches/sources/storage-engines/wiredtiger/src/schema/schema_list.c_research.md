# sources/storage-engines/wiredtiger/src/schema/schema_list.c

Purpose: provides schema handle lookup/release and destruction helpers for tables, tiered handles, column groups, indexes, and layered table resources.

Important APIs and functions: exported helpers include `__wti_schema_get_tiered_uri`, `__wti_schema_release_tiered`, `__wt_schema_get_table_uri`, `__wt_schema_get_table`, `__wti_schema_release_table_gen`, `__wt_schema_release_table`, `__wti_schema_destroy_colgroup`, `__wti_schema_destroy_index`, `__wt_schema_close_table`, `__wt_schema_close_layered`, and `__wt_schema_destroy_layered`.

Control flow: table/tiered lookup saves the current dhandle, opens the requested dhandle with supplied flags, validates incomplete column-group state when requested, returns the typed handle, and restores the caller's dhandle pointer. Release helpers switch to the handle's dhandle and call session release, with optional visibility checks. Destroy helpers free owned names/config/source strings and terminate owned collators. Table close frees plans/formats, column groups, index arrays, resets completion flags, and asserts table-write lock or connection closing. Layered close removes the ingest btree from the layered manager and frees copied config strings; destroy also clears truncate state and destroys the rwlock.

State and persistence behavior: no metadata or disk state is written. The file manages in-memory schema object lifetimes, dhandle references, collator termination side effects, table completeness flags, and layered manager membership.

Dependencies and integration points: used throughout schema create/open/drop/alter/stat code to obtain and release schema handles safely. It depends on session dhandle APIs, table lock flags, collator ABI, layered table manager, and memory ownership conventions for `WT_TABLE`, `WT_INDEX`, `WT_COLGROUP`, and `WT_LAYERED_TABLE`.

Risks: dhandle save/restore is subtle; leaving `session->dhandle` changed can corrupt callers. Releasing tables with the wrong visibility setting can break concurrent schema operations. Index destruction must terminate only owned collators. Table close requires the table write lock to avoid races with cursor open or schema sweeps.

Test signals: handle leak checks, table lookup with incomplete column groups, release with visibility checks, index collator termination, table close during normal schema change and connection close, layered open/close manager membership, and memory sanitizer coverage for repeated open/drop cycles.
