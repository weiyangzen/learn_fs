# sources/storage-engines/wiredtiger/test/suite/test_bug031.py

Purpose: regression for WT-10717/WT-10522 interactions where an original stable update could be missed when the update chain contains aborted updates with `WT_UPDATE_RESTORED_FROM_DS`.

Important APIs/types/functions: `make_scenarios`, timestamp APIs, `reopen_conn` rollback behavior, debug eviction cursor, and timestamped read transactions.

Control flow: insert key at timestamp 10; delete at 20; evict; insert at 30; checkpoint; reopen with stable timestamp 10 causing later updates to abort; start an uncommitted insert and evict to perform update restore; commit it at 40; evict again; then read at timestamp 10 and require the key to be found.

State/persistence behavior: the test deliberately walks the update chain through datastore restore, history store movement, rollback-to-stable, aborted update retention, and a new committed insert. The invariant is that the timestamp-10 original value is not lost when reconciling around aborted restored entries.

Dependencies/integration: row and column scenarios, history store, eviction/reconciliation, checkpoint, and timestamp reads.

Risks/test signals: failure is `WT_NOTFOUND` at timestamp 10 or an eviction assertion. The extensive comments document expected update-chain/disk/HS states and are part of the test's value.
