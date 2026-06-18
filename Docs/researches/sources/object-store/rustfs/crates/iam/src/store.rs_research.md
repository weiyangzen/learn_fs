# sources/object-store/rustfs/crates/iam/src/store.rs

## Purpose

`store.rs` defines the IAM persistence abstraction and shared serialized data structures used by the IAM manager and concrete stores. It keeps `manager.rs` independent from object storage details while standardizing paths, user types, policy mappings, and group records.

## Important APIs, Types, and Functions

`pub mod object` exposes the object-backed implementation. The `Store` trait is async, cloneable, sendable, sync, and `'static`. It defines the complete persistence contract: generic IAM config save/load/delete; user identity save/load/list/delete and secret lookup; group save/load/list/delete; policy document save/load/list/delete; mapped policy save/load/list/delete; and `load_all()` for full cache hydration.

`UserType` distinguishes `Svc`, `Sts`, `Reg`, and `None`. `prefix()` maps those to IAM directory fragments, while `to_u64()` and `from_u64()` provide stable numeric conversion.

`MappedPolicy` serializes a comma-separated policy mapping. It uses `policy` as the canonical JSON field and accepts legacy `policies`. `updatedAt` is serialized as RFC3339 and accepts legacy `update_at`. `new()` sets version 1 and current timestamp; `to_slice()` and `policy_set()` split non-empty comma values.

`GroupInfo` serializes group version, status, member list, and optional RFC3339 `updatedAt` with legacy alias support. `GroupInfo::new()` creates an enabled version-1 group with current update time.

## Control Flow

This file has no runtime control flow beyond helpers. Its design shapes how callers interact with storage: `manager.rs` can request targeted loads after cache misses, perform full reloads, and save records without knowing whether the backend is object storage or another implementation.

The trait separates user identity from mapped policy, which lets regular users, STS users, service accounts, and groups share the same policy-mapping shape while being persisted under different locations by concrete stores.

## State and Persistence Behavior

`MappedPolicy` and `GroupInfo` are the persistent JSON contracts. Their serde aliases preserve compatibility with older MinIO/RustFS style records. Timestamp serialization through `rustfs_policy::serde_datetime` means output is RFC3339, not an internal numeric timestamp.

`UserType::prefix()` is a logical prefix helper; `object.rs` uses a more detailed path mapping for actual object keys. `UserType::None` exists as a neutral value and maps to empty prefix/numeric zero.

## Dependencies and Integration Points

The trait depends on the IAM `Cache`, local `Result`, `rustfs_policy::auth::UserIdentity`, `rustfs_policy::policy::PolicyDoc`, serde, `HashMap`, `HashSet`, and `time::OffsetDateTime`. It is implemented by `store/object.rs` and consumed heavily by `manager.rs`.

## Risks and Edge Cases

`MappedPolicy::to_slice()` and `policy_set()` do not trim before returning/inserting; they filter on `trim().is_empty()` but preserve original spacing in non-empty values. Inputs like `"readwrite, readonly"` may produce `" readonly"` unless higher layers trim. This can affect policy lookup.

The trait has generic async methods (`save_iam_config`, `load_iam_config`) that make object safety unlikely, so stores are used as generic type parameters rather than trait objects. That matches `IamCache<T>` but constrains dependency injection style.

`UserType::from_u64()` returns `None` for invalid values and `Some(UserType::None)` for zero, so callers must distinguish no conversion from the explicit none variant.

## Test Signals

Tests verify RFC3339 serialization and MinIO-style deserialization for `MappedPolicy` and `GroupInfo`. They provide focused compatibility coverage for persistent JSON shape, but there are no trait conformance tests here; concrete behavior is tested in backend modules.
