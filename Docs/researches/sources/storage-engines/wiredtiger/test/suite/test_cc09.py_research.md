# sources/storage-engines/wiredtiger/test/suite/test_cc09.py

Purpose: verifies checkpoint cleanup reads pages from disk to remove obsolete time-window information only when necessary conditions and heuristic limits allow it.

Important APIs/types/functions: inherits `test_cc_base`, uses scenarios for heuristic limits and cleanup preconditions, dsrc stats `checkpoint_cleanup_pages_read_obsolete_tw` and `checkpoint_cleanup_pages_obsolete_tw`, optional delete, timestamp bumping, and tiered skip.

Control flow: populate 100,000 rows, set stable and checkpoint, advance oldest to make part of the time windows obsolete, reopen so pages are on disk, open/read/reset a cursor to activate the handle, optionally delete one key and checkpoint, optionally advance oldest to the end, force cleanup, then assert read/dirty stats based on `expected_cleanup` and whether delete or oldest bump made cleanup valid.

State/persistence behavior: moves pages to disk before cleanup, then tests disk-read cleanup of obsolete time-window metadata. Deletes and oldest timestamp movement provide the trigger conditions.

Dependencies/integration: checkpoint cleanup disk reads, heuristic controls, timestamp manager, dsrc stats, and large table population.

Risks/test signals: large workload; failures identify missing cleanup, unexpected cleanup without triggers, or too many dirtied pages.
