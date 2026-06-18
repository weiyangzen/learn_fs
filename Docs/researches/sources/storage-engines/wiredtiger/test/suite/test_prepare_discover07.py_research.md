# sources/storage-engines/wiredtiger/test/suite/test_prepare_discover07.py

Purpose: validates the analogous disaggregated layered-table flow for a prepared tombstone transaction, ensuring committed values are deleted on commit and preserved on rollback.

Important APIs and types: `layered:` cursor, `prepared_discover:`, `claim_prepared_id`, `wiredtiger.WT_NOTFOUND`, disaggregated leader/follower configuration, checkpoint metadata, and commit/rollback scenarios.

Control flow: leader commits keys 1-6, prepares removes for keys 4-6 with id 123, checkpoints with stable timestamp after the prepare, and reopens as a follower from checkpoint metadata. The follower discovers and claims the id, commits or rolls back it, then reads at timestamp 60 and 200/220 to assert final state.

State and persistence behavior: the prepared tombstone is captured in the stable checkpoint chain. Commit resolution makes keys 4-6 not found at later read timestamps; rollback resolution restores their committed values.

Dependencies and integration points: disaggregated storage, layered table ingest/stable components, prepare discovery, timestamped deletion visibility, and role handoff.

Risks: the source contains a `self.session.breakpoint()` inside validation, which may be intentional debug support but is notable because breakpoints can affect automated runs depending on harness behavior.

Test signals: exactly one id 123 is discovered, baseline keys always read correctly, and keys 4-6 match the expected found/not-found behavior for commit versus rollback.
