# sources/object-store/rustfs/crates/protocols/src/swift/quota.rs

## Purpose
`quota.rs` enforces Swift container quota metadata during uploads. It supports byte quotas and object-count quotas configured through container metadata.

## Important APIs, Types, And Functions
`QuotaConfig` stores optional `quota_bytes` and `quota_count`. `QuotaConfig::load` fetches container metadata and parses `x-container-meta-quota-bytes` and `x-container-meta-quota-count`. `is_enabled` checks whether either limit exists. `check_quota` uses saturating arithmetic to reject uploads that exceed byte or count limits with `RequestEntityTooLarge`. `check_upload_quota` loads config and current usage before enforcing. The module-level `is_enabled` helper suppresses metadata lookup errors and reports false.

## Control Flow
`handler.rs` calls `check_upload_quota` only for object PUT requests with a parseable `Content-Length`. The quota check loads container metadata twice: once for quota metadata and once for current usage. If enabled, it compares current bytes/count plus the new object size/count against configured limits before object storage upload starts.

## State, Persistence, And Dependencies
Quota configuration and usage are stored in container metadata and container stats maintained by the container/storage modules. This module persists nothing directly. It depends on Swift container metadata APIs, credentials, tracing, and `SwiftError`.

## Integration Points
The handler integrates quota on regular object PUT before version archiving and object upload. FormPost uploads call `object::put_object` directly from `formpost.rs`, so quota enforcement depends on whether they pass through handler checks; in this code path they do not. Unknown-size streaming uploads are also not quota checked because there is no content-length.

## Risks And Test Signals
Quota enforcement is best-effort and race-prone: concurrent uploads can pass checks against stale usage, and count quotas increment by one even for overwrites. Invalid quota metadata silently disables the malformed limit because parsing uses `.ok()`. Content-length absence bypasses enforcement. Tests thoroughly cover quota arithmetic, exact limits, zero limits, both dimensions, and overflow saturation, but not metadata loading or concurrent upload races.
