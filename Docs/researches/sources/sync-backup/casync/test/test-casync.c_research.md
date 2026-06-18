# sources/sync-backup/casync/test/test-casync.c

Purpose: high-level library API test for `CaSync` encode/decode workflows.

Important APIs/types/functions: creates temp tree/store/index paths, runs encode with feature flags, base fd, archive digest, store path, and index path; then runs decode with the same store/index and validates archive digest retrieval.

Control flow/state: drives `ca_sync_step` state machine until finished, handling archive digest states and cleaning temporary index/store/tree with `rm_rf`.

Dependencies/integration: exercises core casync orchestration, store/index interaction, feature flags, digest reporting, and cleanup utilities.

Risks/test signals: strong end-to-end API signal, though the generated source tree is small. Failures identify state machine, file setup, or digest regressions.

Source research group: `subset-b-009122`.
