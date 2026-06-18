# sources/storage-engines/wiredtiger/src/schema/schema_truncate.c

## Purpose
Implements schema-level truncate dispatch for whole objects and cursor ranges. It maps public `WT_SESSION::truncate` requests onto file, table, tiered, layered, history-store, table, and extension data-source implementations, including fallback cursor-walk removal for data sources that lack a native truncate hook.

## Important APIs, Types, and Functions
- `__wt_schema_truncate(session, uri, cfg)` is the no-range schema dispatcher. It expects checkpoint and schema locks to be held, routes by URI prefix, and maps `WT_NOTFOUND` to `ENOENT`.
- `__wt_schema_range_truncate(WT_TRUNCATE_INFO *)` dispatches range truncation by object type, including history store, file/btree, table, layered, extension `range_truncate`, and generic cursor iteration.
- `__wt_range_truncate(start, stop)` is the generic cursor-based implementation. With no start cursor it removes backward from `stop`; otherwise it removes forward from `start` until it reaches `stop`.
- `__truncate_table`, `__truncate_tiered`, `__truncate_layered`, and `__truncate_dsrc` implement whole-object truncation for composite or non-file data sources.
- `WT_TRUNCATE_INFO` carries session, URI, explicit start/stop flags, cursors, and original key buffers to downstream btree/table/layered truncate code.

## Control Flow
Whole-object truncate first distinguishes btree files, layered tables, regular tables, tiered data sources, and extension data sources. Table truncate recursively truncates every column group and then every opened index. Tiered truncate obtains an exclusive dhandle and calls range truncate without a current dhandle. Layered whole truncate opens cursors for first and last visible keys and records a range truncate entry. Unsupported or unknown URI types are rejected through shared error helpers.

Range truncate special-cases the history store, ingest replay for file URIs, btree file ranges with required key validation, table ranges, layered ranges on leaders or non-slow followers, extension `range_truncate`, and finally the generic cursor remove loop. Layered range truncate resolves a missing stop cursor to the table's last visible key because layered truncate-list entries require concrete bounds.

## State and Persistence Behavior
This file does not own durable metadata updates, but it drives durable effects through lower layers: btree truncate, table truncate, history-store truncate, layered truncate-list recording, extension data-source hooks, and cursor remove calls. Statistics (`cursor_truncate`) are incremented for whole-object paths. It also carefully releases schema tables, dhandles, and local cursors on error paths.

## Dependencies and Integration Points
Depends on schema table/index lookup, cursor opening, dhandle acquisition/release, btree truncate, table range truncate, history-store cursor truncate, layered table truncate, and data-source extension hooks from `WT_DATA_SOURCE`. It is called by `session_api.c` through `__wt_session_range_truncate` and the schema locked section of `WT_SESSION::truncate`.

## Risks
Range-bound correctness is high risk: missing `__cursor_needkey`, wrong `WT_TRUNC_EXPLICIT_STOP`, or incorrect start/stop comparisons can delete too much or too little data. Layered truncate has explicit FIXME debt around local stop-cursor creation. Whole-table truncate must maintain table/index/colgroup consistency. Extension data sources can supply partial behavior, so fallback behavior must not silently bypass custom semantics.

## Test Signals
Useful coverage includes truncate by URI and by cursor bounds, empty ranges, start-after-stop validation, table-with-index truncate, layered leader/follower behavior, tiered truncate, history-store truncate, extension source fallback and native hooks, and recovery/logging tests that confirm truncation persists correctly.
