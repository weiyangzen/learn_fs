# sources/object-store/rustfs/crates/targets/src/domain.rs

## Purpose
Small domain mapping module that names the two logical target plugin domains RustFS supports: notification targets and audit targets.

## Important APIs, types, and functions
- `TargetDomain::{Notify, Audit}` serializes with snake_case names.
- `runtime_target_type` maps domains to `TargetType::NotifyEvent` or `TargetType::AuditLog`.
- `impl From<TargetType> for TargetDomain` maps runtime target types back into domain values.

## Control flow
The conversion logic is a pair of total `match` expressions over the currently known target types.

## State and persistence behavior
No state is persisted. The enum is serde-compatible and can appear in manifests, handshakes, and admin records.

## Dependencies and integration points
It depends on `crate::target::TargetType` and is used by manifests, instance descriptors, sidecar handshakes, and control-plane policy checks.

## Risks and edge cases
The `From<TargetType>` implementation assumes every `TargetType` belongs to one of these domains. If more target types are added, this conversion must be updated or compilation will fail.

## Test signals
There are no direct tests. Coverage is indirect through sidecar, manifest, and instance-normalization tests that compare expected domains.
