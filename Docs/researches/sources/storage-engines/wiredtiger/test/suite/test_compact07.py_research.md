# sources/storage-engines/wiredtiger/test/suite/test_compact07.py

Purpose: validates background compaction selects only files whose free space exceeds the configured threshold, and that foreground compaction can later compact a smaller-free-space file.

Important APIs and types: `compact_util`, `stat.conn.background_compact_files_tracked`, `stat.dsrc.block_reuse_bytes`, `get_files_compacted`, `get_pages_rewritten`, `turn_on_bg_compact`, and `dropUntilSuccess`.

Control flow: create one table with 20 percent deleted and two tables with 90 percent deleted; compare free-space MB; run background compaction once with threshold above the small table's free space; verify only large-free-space tables compacted; run foreground compaction on the small table; then restart background tracking and drop tables until tracking list shrinks.

State and persistence behavior: background compaction tracks metadata files, skips those below threshold, rewrites eligible files, and drops removed tables from tracking after idle expiration.

Dependencies and integration points: background compact debug mode, block reuse statistics, foreground compact helper, and table drop handling. Tiered hook is skipped.

Risks: loops wait on asynchronous background stats. A small bug in the free-space comparison loop references the last `uri` value but scenario intent is clear.

Test signals: small table has zero pages rewritten by background then positive pages after foreground; skipped and success stats are positive; tracking count eventually drops.
