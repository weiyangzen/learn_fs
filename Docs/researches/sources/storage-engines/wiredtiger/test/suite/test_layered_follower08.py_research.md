<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_follower08.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_follower08.py

Purpose: tests delete behavior on a follower's ingest table for layered tables.

Important APIs/types/functions: uses `wiredtiger.WT_NOTFOUND`, scenarios for string (`S`) and integer (`I`) value formats, a local `value` converter, and follower config with `disaggregated=(lose_all_my_data=true)` plus follower role.

Control flow: the test creates a `layered:test_layered_follower08` table with string keys and scenario value format. It inserts keys `"0"` through `"99"` directly into the follower ingest table, then removes each key through the same layered cursor. It resets the cursor, checks `next()` returns not found, and point-searches every key to ensure removal.

State and persistence behavior: all records are follower-local ingest records; deletes should leave the layered table logically empty for both scan and point-read paths.

Dependencies/integration points: exercises follower ingest deletes independent of stable checkpoints and across value encodings. Risks are lack of explicit transactions around inserts/removes, relying on autocommit semantics. Test signals are successful removes and WT_NOTFOUND for full scan and all point searches.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_follower08.py -->
