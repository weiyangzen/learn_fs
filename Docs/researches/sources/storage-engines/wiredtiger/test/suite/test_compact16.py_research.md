# sources/storage-engines/wiredtiger/test/suite/test_compact16.py

Purpose: tests foreground compaction can reclaim space while checkpoints are running concurrently, without exhausting compact pass limits and leaving excessive reusable space.

Important APIs and types: `compact_util`, `checkpoint_thread`, `stat.conn.checkpoint_state`, `session.compact`, `get_bytes_avail_for_reuse`, and `get_size`.

Control flow: create and populate a million-key table, checkpoint, delete one quarter, reopen to force disk state, start a background checkpoint thread and wait for it to enter checkpoint state, run compact concurrently, stop the checkpoint thread, then calculate percentage available for reuse.

State and persistence behavior: compaction and checkpoint can contend over block movement and checkpoint writes. The expected result is successful space reclamation despite concurrent checkpoint activity.

Dependencies and integration points: foreground compaction, checkpoint threading, block reuse statistics, verbose compact output suppression, and compact helper population/deletion. Tiered hook is skipped.

Risks: high data volume and concurrent timing are expensive and potentially flaky. It uses a percentage threshold rather than exact file size.

Test signals: reusable bytes divided by file size is less than 20 percent after compact.
