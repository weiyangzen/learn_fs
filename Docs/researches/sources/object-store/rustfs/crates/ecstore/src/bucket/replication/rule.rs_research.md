# sources/object-store/rustfs/crates/ecstore/src/bucket/replication/rule.rs

## Purpose
This file extends the S3 `ReplicationRule` DTO with RustFS-specific convenience logic for extracting a rule prefix and deciding whether replica metadata changes should be replicated.

## Important APIs, Types, and Functions
- `ReplicationRuleExt` defines `prefix(&self) -> &str` and `metadata_replicate(&self, obj: &ObjectOpts) -> bool`.
- `prefix` reads `rule.filter.prefix` first, then `rule.filter.and.prefix`, and defaults to an empty string.
- `metadata_replicate` returns true for non-replica objects and for replica objects only when source-selection criteria enables replica modifications.

## Control Flow and State Behavior
The implementation is pure and stateless. It walks optional nested DTO fields and compares `ReplicaModificationsStatus` to `ENABLED`. No mutation or I/O occurs.

## Dependencies and Integration Points
It depends on `s3s::dto::{ReplicationRule, ReplicaModificationsStatus}` and local replication `ObjectOpts`. Replication rule matching and replication admission code can use it to keep DTO interpretation centralized.

## Persistence
No persistence. It interprets an in-memory replication configuration object.

## Risks and Edge Cases
Empty string is both the default and the representation for no prefix, so callers must distinguish whole-bucket rules by convention. The `metadata_replicate` path clones `replica_modifications`; that is low risk but unnecessary. The function only checks replica modification enablement and does not validate destination, status, delete-marker behavior, tags, or other filter constraints.

## Test Signals
No inline tests. Useful tests would cover filter prefix precedence, `and.prefix` fallback, absent filters, replica/non-replica objects, and disabled or absent replica-modification criteria.
