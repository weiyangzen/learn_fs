# sources/object-store/rustfs/crates/ecstore/src/tier/tier_config.rs

## Purpose

Defines tier configuration serde models, provider-specific credential/location structs, type conversion helpers, redacted cloning, and small builder helpers.

## Important APIs and Types

`TierType` covers S3, RustFS, MinIO, Aliyun, Tencent, Huawei Cloud, Azure, GCS, R2, and unsupported, with display/lowercase helpers. `TierConfig` holds version/type/name plus optional provider payloads. Provider structs include `TierS3`, `TierRustFS`, `TierMinIO`, `TierAliyun`, `TierTencent`, `TierHuaweicloud`, `TierAzure`, `TierGCS`, and `TierR2`; Azure also has `ServicePrincipalAuth`.

## Control Flow

`TierConfig::clone` branches on active `tier_type`, clones only that payload, and redacts secrets or GCS creds. Private endpoint/bucket/prefix/region helpers branch similarly. `TierAzure::is_sp_enabled` checks required SP fields.

## State and Persistence Behavior

These structs are persisted through tier config serialization. Redaction only applies to clones returned/listed by callers, not the original in-memory or persisted config.

## Dependencies and Integration Points

Used by `tier.rs` persistence/admin logic and all warm-backend constructors.

## Risks and Edge Cases

Custom `Clone` is not a full fidelity clone for reuse because it redacts secrets and drops inactive payloads. `TierType::new` accepts display-case strings, not serde lowercase. Some construction helpers are dead code, and Azure SP option code is only commented reference.

## Test Signals

No direct tests; round-trip tests in `tier.rs` partially cover serde compatibility.
