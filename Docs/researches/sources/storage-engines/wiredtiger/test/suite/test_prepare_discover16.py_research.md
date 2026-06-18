# sources/storage-engines/wiredtiger/test/suite/test_prepare_discover16.py

Purpose: validates that a prepared delete captured by a checkpoint and rolled back through follower discovery leaves the original committed stable value readable by a fresh follower after post-rollback checkpointing.

Important APIs and types: `stable_uri`, helper methods `_open_follower`, `_checkpoint`, `_discover_and_claim`, direct cursor open on `file:<tablename>.wt_stable`, `prepared_discover:`, `claim_prepared_id`, and `wiredtiger.WiredTigerError` handling.

Control flow: the leader creates a layered table, commits many keys, prepares a delete of target key 500 with a prepared id, checkpoints while prepared, and closes without final checkpoint. The follower discovers and claims the prepared id, rolls it back, steps up, advances stable, checkpoints, captures post-rollback metadata, closes, and opens a fresh follower. The fresh follower reads the stable constituent directly at timestamp 300.

State and persistence behavior: the rollback must be encoded durably in the stable checkpoint chain, not only masked by ingest state. Directly reading the stable file checks the underlying committed value.

Dependencies and integration points: layered stable constituent files, disaggregated checkpoint metadata, prepared delete rollback, fresh follower open, and timestamped reads.

Risks: direct access to `*.wt_stable` is tightly coupled to layered table implementation details but gives stronger evidence than reading the layered URI.

Test signals: discovery returns the expected id; fresh follower open succeeds; searching target key in the stable URI returns 0 and value `committed_value`.
