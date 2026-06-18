<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_follower04.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_follower04.py

Purpose: ensures a follower picking up a checkpoint adds the stable component of a layered table, and that this works after role reversal.

Important APIs/types/functions: uses `disagg_advance_checkpoint`, direct `conn.reconfigure` role switches, precise checkpoint config, and scenarios for native `layered:` and table-layered URIs.

Control flow: the initial node starts as follower, steps up to leader, creates a follower connection, and creates matching tables. The leader writes 5000 rows and checkpoints; before checkpoint advance, only the leader sees the rows. After `disagg_advance_checkpoint`, the follower sees them. Then the follower is promoted to leader and the old leader steps down. The new leader writes another 5000 rows and checkpoints; the old leader only sees old rows until checkpoint advance, after which it sees all rows.

State and persistence behavior: checkpoint pickup materializes stable table content on the follower; role switch preserves and extends the stable component.

Dependencies/integration points: integrates role transitions, precise checkpoint timestamp setup, and layered/table-layered creation. Risks are missing timestamp updates before precise checkpoint. Test signals are scan item counts before and after checkpoint pickup in both directions.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_follower04.py -->
