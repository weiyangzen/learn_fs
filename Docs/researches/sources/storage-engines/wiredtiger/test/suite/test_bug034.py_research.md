# sources/storage-engines/wiredtiger/test/suite/test_bug034.py

Purpose: regression for WT-12602, where evicting a page in parallel with checkpoint could incorrectly return `EBUSY` when history store content included a globally visible tombstone and newer modify/update entries.

Important APIs/types/functions: `wiredtiger.Modify`, `debug_mode=(eviction_checkpoint_ts_ordering=true)`, helper `evict_cursor`, `session.checkpoint`, timestamped and non-timestamped transactions.

Control flow: two tests build similar non-timestamped and timestamped chains. They insert base data, checkpoint it, remove all keys to create tombstones, add updates plus modifies, update again to push update/modify/tombstone content to the history store, checkpoint, then dirty the data and call debug eviction across all keys.

State/persistence behavior: targets history store reconciliation ordering when checkpoint timestamp ordering is simulated. The history store must accept tombstone/update/modify combinations without reporting an artificial busy condition.

Dependencies/integration: modify API, history store, checkpoint, eviction debug mode, global visibility via non-timestamped tombstones or advanced oldest timestamp.

Risks/test signals: absence of assertions means the key signal is no exception during dirty eviction. It covers both non-timestamp and timestamp semantics.
