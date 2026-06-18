# sources/object-store/rustfs/crates/ecstore/src/bucket/replication/mod.rs

Purpose: Assembles the replication subsystem module tree and re-exports its public API.

Important APIs and types: Private modules include `config`, `replication_pool`, `replication_resyncer`, `replication_state`, and `rule`; `datatypes` is public. The file re-exports config extensions, datatypes, pool/resyncer APIs, `BucketStats` from replication state, and rule extensions.

Control flow and state: No runtime logic. It determines which replication internals are visible to the rest of `ecstore`.

Dependencies and integration: Downstream modules import replication decisions, resync helpers, and state through this module. `migration.rs` imports `decode_resync_file` and `encode_resync_file` from the re-exported replication API.

Risks: Broad `pub use` exports can make internal types part of the effective crate API and increase coupling. Private module declarations still expose many items through re-exports.

Test signals: No direct tests. Compilation and tests in child modules validate this wiring.
