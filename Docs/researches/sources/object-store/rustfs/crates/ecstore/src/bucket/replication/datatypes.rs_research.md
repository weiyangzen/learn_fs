# sources/object-store/rustfs/crates/ecstore/src/bucket/replication/datatypes.rs

Purpose: Defines shared replication resync status values and their display strings.

Important APIs and types: `ResyncStatusType` enum includes `NoResync`, `ResyncPending`, `ResyncCanceled`, `ResyncStarted`, `ResyncCompleted`, and `ResyncFailed`. `is_valid` treats every value except `NoResync` as valid. `Display` maps statuses to user-facing strings such as `Ongoing`, `Completed`, `Failed`, `Pending`, and `Canceled`.

Control flow and state: Stateless enum helpers. Serialization derives allow the status to appear in persisted replication state and API responses.

Dependencies and integration: Used by replication resync state and migration normalization of `.replication/resync.bin`. Re-exported by `replication/mod.rs`.

Risks: `NoResync` displays as an empty string, so UI/API consumers must not confuse it with missing data. Adding statuses requires updating both `is_valid` and `Display`.

Test signals: No direct tests in this file. Migration tests indirectly exercise resync status encode/decode around this type.
