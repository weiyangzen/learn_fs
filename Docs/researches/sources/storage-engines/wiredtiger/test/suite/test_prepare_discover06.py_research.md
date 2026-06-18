# sources/storage-engines/wiredtiger/test/suite/test_prepare_discover06.py

Purpose: tests prepared transaction discovery for layered tables in disaggregated storage, with leader checkpoint handoff to a follower and commit/rollback resolution.

Important APIs and types: `@disagg_test_class`, `gen_disagg_storages`, `layered:` URI, `disaggregated=(role="leader"/"follower",checkpoint_meta=...)`, `disagg_get_complete_checkpoint_meta`, `prepared_discover:`, and `claim_prepared_id`.

Control flow: the leader creates a layered table, writes baseline committed data, prepares additional inserts, advances stable, checkpoints, captures checkpoint metadata, and reopens as a follower using that metadata. The follower verifies committed data, discovers the prepared id, claims it, commits or rolls it back according to scenario, advances stable, and verifies reads after resolution.

State and persistence behavior: prepared updates are persisted in the disaggregated checkpoint and transferred via checkpoint metadata rather than a backup directory. The test validates that follower resolution changes layered-table visibility consistently after stable advancement.

Dependencies and integration points: disaggregated storage helper infrastructure, layered table support, prepared metadata preservation, timestamped reads, and role reconfiguration.

Risks: layered/disaggregated tests are sensitive to checkpoint metadata format and role semantics. Scenario expansion can be expensive because it combines storage variants with commit/rollback resolution.

Test signals: committed keys remain visible at old timestamps, exactly one prepared id is discovered, and prepared keys are visible only for commit resolution and absent for rollback resolution at later timestamps.
