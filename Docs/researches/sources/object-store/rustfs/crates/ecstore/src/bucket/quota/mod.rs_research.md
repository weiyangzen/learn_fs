# sources/object-store/rustfs/crates/ecstore/src/bucket/quota/mod.rs

Purpose: Defines the bucket quota configuration schema, quota operation/result types, and public error response contract.

Important APIs and types: `QuotaType` currently supports only `Hard`, with serde aliases for uppercase/lowercase compatibility. `BucketQuota` stores optional byte limit, quota type, created timestamp, and optional updated timestamp. Methods include `marshal_msg`, `unmarshal`, `new`, `get_quota_limit`, `check_operation_allowed`, and `get_remaining_quota`. `QuotaCheckResult`, `QuotaOperation`, `QuotaError`, and `QuotaErrorResponse` define enforcement outcomes and API errors.

Control flow and state: The module is mostly data modeling. `BucketQuota::new` stamps `created_at` with current UTC time. Quota checks allow all operations when `quota` is `None`; otherwise they use saturating addition/subtraction helpers where implemented.

Dependencies and integration: Re-exports `checker`. Uses `rustfs_config` error code constants and API path, `serde`, `thiserror`, and `time` RFC3339 serde. `metadata.rs` stores this schema as `quota.json`; `QuotaChecker` enforces it.

Risks: Only hard quota exists, so future soft quota behavior would require enum and checker updates. `check_operation_allowed` uses saturating addition, while checker expected usage uses normal addition. Error response intentionally uses PascalCase fields; changing serde names would break external contract.

Test signals: Unit tests cover legacy quota JSON without quota_type, RustFS format, uppercase `HARD`, marshal/unmarshal, and PascalCase error response serialization.
