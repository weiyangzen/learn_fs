# sources/storage-engines/wiredtiger/test/suite/test_compact01.py

Purpose: validates session-level and utility compaction reduce page count after deleting most of a file or complex table.

Important APIs and types: `compact_util`, `suite_subprocess`, `SimpleDataSet`, `ComplexDataSet`, `runWt(["compact", ...])`, `session.compact`, `stat.dsrc.btree_row_leaf`, and compact progress stats.

Control flow: populate a dataset with many entries, reopen to force disk state, assert enough leaf pages exist, truncate most keys, compact via session method or `wt compact`, optionally after reopen, then reopen and check page count decreased below scenario threshold.

State and persistence behavior: compaction should rewrite/reclaim on-disk pages after deletion. Utility-mode compaction requires closing the connection and running the external tool.

Dependencies and integration points: uses compact progress stats for method mode, skip for timestamp hook because timestamped removals do not free space, and avoids progress stat checks for tiered/utility cases.

Risks: compaction behavior depends on page sizing, overflow avoidance, and storage hook behavior. Utility invocation depends on `suite_subprocess`.

Test signals: initial page count is above `maxpages`; after compaction and reopen, row leaf page count is below `maxpages`; method mode reports reviewed/rewritten progress.
