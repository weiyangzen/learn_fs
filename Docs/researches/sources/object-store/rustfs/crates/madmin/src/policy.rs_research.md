# sources/object-store/rustfs/crates/madmin/src/policy.rs

Purpose: defines the admin policy-info wire schema.

Important APIs/types/functions: `PolicyInfo` contains `policy_name`, arbitrary JSON `policy`, and optional `create_date`/`update_date` timestamps. It derives serde traits and `Debug`.

Control flow: no executable logic. Serde omits absent dates, allowing old or partial admin responses to carry just the name and policy JSON.

State and persistence: no persistence. The module represents policy state returned by or sent to admin endpoints. The policy body stays as `serde_json::Value`, leaving semantic validation to IAM/policy code outside this crate.

Dependencies/integration: depends on serde, `serde_json::Value`, and `time::OffsetDateTime`. It is glob re-exported by `lib.rs`, making `PolicyInfo` part of the crate’s top-level public contract.

Risks: arbitrary JSON means malformed policy semantics can pass this layer. Optional timestamps do not use an explicit serde RFC3339 adapter here, so compatibility depends on `time` serde behavior enabled in the workspace.

Test signals: no local tests. Validation is indirect through downstream policy parsing and serde compilation.
