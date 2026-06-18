# sources/storage-engines/wiredtiger/test/suite/test_layered_delta05.py

Purpose: validates internal page delta writing and reading for disaggregated file tables under configurations that enable leaf only, internal only, both, or neither page-delta type.

Important APIs and functions: `test_layered_delta05` uses `page_delta=(delta_pct=100)`, small page sizes with `block_manager=disagg`, `stat.conn.rec_page_delta_leaf`, `stat.conn.rec_page_delta_internal`, `stat.conn.cache_read_internal_delta`, and helpers `insert`, `verify`, and `get_stat`.

Control flow: `test_internal_page_delta_simple` populates 1000 rows, reopens to force disk reads, updates a few keys, checkpoints, checks write statistics by configured delta type, reopens as leader and follower, and verifies internal delta reads. `test_internal_page_delta_split_internal` expands selected keys to force splits, then shrinks them to encourage internal-page merge deltas and verifies after reopen.

State and persistence behavior: the tests drive base images, leaf updates, and internal tree shape changes. Reopen clears cache so verification must reconstruct from stored full images and page deltas. Follower mode checks the same persisted state from a disaggregated consumer role.

Dependencies and integration: integrates page reconciliation, internal/leaf delta toggles, connection statistics, disaggregated reopen helpers, and page split/merge behavior. Risks include writing deltas despite disabled configuration, failing to read internal deltas, losing split/merge keys, and stat mismatches. Test signals combine statistic thresholds with full-table value verification.
