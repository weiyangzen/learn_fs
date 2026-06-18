<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_scrub_eviction_prepare.py -->
# sources/storage-engines/wiredtiger/test/suite/test_scrub_eviction_prepare.py

Purpose: verifies that scrub eviction of a page containing a prepared update writes the prepared state cleanly enough that later checkpoints do not repeatedly reconcile the leaf page.

Important APIs/types/functions: `test_scrub_eviction_prepare` uses `wttest.skip_for_hook`, multiple sessions, prepared transactions, `debug=(release_evict)`, `session.checkpoint`, and data-source statistic `stat.dsrc.btree_checkpoint_pages_reconciled`. Connection config enables all stats and JSON stats logging.

Control flow: create an integer/string table, insert key 2 committed in one session, prepare an update for key 1 in another session, close the updating cursor, release-evict key 2 to evict the page containing both keys, checkpoint, record reconciled pages, read key 2 to fault the page back in, checkpoint twice more, and assert the reconciled page count remains 1.

State and persistence behavior: prepared update state is persisted by scrub eviction and re-instantiated cleanly. The test avoids prepared conflicts by reading key 2, not key 1.

Dependencies/integration points: integrates prepare, eviction, scrub/reconciliation, checkpoint stats, and session isolation; tiered is skipped. Risks include eviction not happening if cursors pin pages, which the test addresses by closing the cursor. Signals are stable reconciliation stats across repeated reads/checkpoints.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_scrub_eviction_prepare.py -->
