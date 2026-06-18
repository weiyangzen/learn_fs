# sources/object-store/rustfs/crates/ecstore/src/bucket/lifecycle/bucket_lifecycle_audit.rs

Purpose: small lifecycle audit model that attaches a lifecycle event source to a lifecycle event.

Important APIs and types: `LcEventSrc` enumerates origin categories: none, heal, scanner, decom, rebalance, and S3 operations such as head/get/list/put/copy/complete-multipart. `LcAuditEvent` contains a `lifecycle::Event` and source. `LcAuditEvent::new` constructs the pair.

Control flow: no complex logic; default source is `None`, and default event comes from `lifecycle::Event` default.

State and persistence: purely in-memory struct definitions. If audit events are serialized elsewhere, this file defines the source taxonomy.

Dependencies and integration points: depends on `crate::bucket::lifecycle::lifecycle` for the actual lifecycle event type. Intended integration points are lifecycle scanner, healing, decommission/rebalance, and S3 API paths that trigger lifecycle decisions.

Risks: enum variants are not explicitly serialized here; compatibility depends on downstream serde or formatting if added. Missing source variants can reduce audit specificity for future lifecycle triggers.

Test signals: no direct tests; correctness depends on call sites populating the correct `LcEventSrc`.
