<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/prepared_discover/prepared_discover_walk.c -->
# sources/storage-engines/wiredtiger/src/prepared_discover/prepared_discover_walk.c

## Purpose
Scans metadata and btrees to discover prepared updates after startup/recovery and attach them to pending transaction structures.

## Important APIs, Types, and Functions
`__wt_prepared_discover_filter_apply_handles` is the entry point. Helpers parse checkpoint metadata, decide disaggregated follower stable walks, open ingest cursors, inspect on-disk cells/update lists/insert lists, skip tree branches without prepare metadata, and walk one tree.

## Control Flow
The entry point iterates metadata btree URIs, filters those whose checkpoint config has `prepare=true`, converts stable follower URIs to a latest-checkpoint URI, and walks each tree. Tree walking opens the dhandle, optionally opens the paired ingest cursor, uses `__wt_tree_walk_custom_skip` with visible-all/no-evict flags, and processes leaf pages. Row-store pages scan insert lists, update chains, and disk cells; prepared update chains stop at the first non-prepared update.

## State and Persistence Behavior
Discovers and records in-memory pending prepared operations. On disaggregated followers, on-disk stable prepared cells are restored into ingest before registration. History-store artifacts are ignored unless associated data-store records are found.

## Dependencies and Integration Points
Depends on metadata cursors, checkpoint metadata parsing, tree walk, page/cell unpacking, update visibility, row-store keys, prepared-discover transaction helpers, and layered table naming conventions.

## Risks and Edge Cases
Column-store prepared discovery and prepared truncate are explicitly unsupported and assert. Skipping relies on time-aggregate prepare bits; wrong metadata can miss pages. Follower restoration assumes `.wt_stable` to `.wt_ingest` URI derivation.

## Test Signals
Recovery tests with prepared row-store updates, disaggregated follower restore tests, metadata prepare filtering, branch-skip correctness, unsupported column/truncate fatal paths, and history-store interactions are key.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/prepared_discover/prepared_discover_walk.c -->
