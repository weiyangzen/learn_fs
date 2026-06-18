# sources/storage-engines/wiredtiger/test/suite/test_cc07.py

Purpose: verifies checkpoint cleanup removes obsolete time-window information from pages and respects heuristic limits on btrees/pages per checkpoint.

Important APIs/types/functions: inherits `test_cc_base`, uses `make_scenarios`, connection config `heuristic_controls=[obsolete_tw_btree_max=...]` and `checkpoint_cleanup_obsolete_tw_pages_dirty_max=...`, dsrc/conn stat `checkpoint_cleanup_pages_obsolete_tw`, and tiered skip.

Control flow: for each heuristic scenario, append 10 batches of 1,000 1KB values, checkpoint after each batch, and advance stable/oldest to make time windows obsolete. Force cleanup, read per-btree and connection obsolete-time-window cleanup stats, and assert either zero cleanup when limits are disabled or positive cleanup bounded by the configured maximum.

State/persistence behavior: repeated timestamp advancement makes earlier start time windows globally visible and removable. Cleanup should dirty only up to the configured number of pages.

Dependencies/integration: checkpoint cleanup heuristics, time-window reconciliation, statistics logging, and timestamped population helper.

Risks/test signals: failures indicate cleanup ignores disable settings, fails to clean when enabled, or exceeds page dirtying limits.
