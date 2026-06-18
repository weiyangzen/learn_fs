# sources/storage-engines/wiredtiger/test/suite/test_compact12.py

Purpose: intended to verify compaction rewrites pages in `WT_REF_DELETED` state that still have disk blocks, especially after a mix of obsolete deletes and non-obsolete fast truncate.

Important APIs and types: `compact_util`, `test_cc_base`, timestamped populate/remove/truncate, `wait_for_cc_to_run`, `stat.conn.rec_page_delete_fast`, `session.compact`, and `get_size`.

Control flow: the active test immediately skips due to FIXME-SLS-1890. The intended flow creates and populates timestamped data, deletes the first quarter and makes it obsolete, fast-truncates the last tenth, waits for checkpoint cleanup, verifies fast truncate pages, compacts, and checks that at least one quarter of file size is recovered.

State and persistence behavior: the intended persistence target is reclaiming disk blocks for deleted references after checkpoint cleanup and compaction.

Dependencies and integration points: checkpoint cleanup, fast truncate, foreground compaction, timestamps, and size accounting. Tiered hook would be skipped before the explicit skip.

Risks: currently disabled because it is not robust to eviction behavior. As a result it provides no active regression coverage until re-enabled.

Test signals: currently the only runtime signal is a skip. If enabled, it would require positive fast-truncate pages and size recovery above one quarter of pre-compact size.
