# sources/storage-engines/wiredtiger/test/suite/test_bug030.py

Purpose: regression for WT-10522 involving aborted tombstones restored from the data store. It ensures reconciliation does not return early when appending a key's original value to an update list.

Important APIs/types/functions: `make_scenarios` for column and integer row formats, `debug_mode=(update_restore_evict=true)`, timestamp APIs, debug eviction cursor `debug=(release_evict)`, `session.checkpoint`, and `reopen_conn`.

Control flow: insert stable values at timestamp 10; set oldest/stable; delete all rows at timestamp 30; evict; write unstable updates at 50; checkpoint and reopen, which rolls back unstable state; delete again at 60; evict all rows at timestamp 70. The final eviction is the regression trigger.

State/persistence behavior: constructs an update chain containing an aborted, restored-from-datastore entry and then reconciles it. The persistence invariant is that original stable values remain reconstructable and reconciliation does not mishandle aborted tombstone flags.

Dependencies/integration: rollback-to-stable during reopen, update restore eviction debug mode, timestamped deletes/updates, and reconciliation.

Risks/test signals: no explicit final read; crashes/assertions during eviction are the signal. Scenario covers both row-store and column-store keys.
