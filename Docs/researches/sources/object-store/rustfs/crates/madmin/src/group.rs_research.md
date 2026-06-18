<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/madmin/src/group.rs -->
# sources/object-store/rustfs/crates/madmin/src/group.rs

Purpose: `group.rs` defines admin payload structures for group membership/status operations and group descriptions.

Important APIs/types/functions: `GroupStatus` is a lower-case serde enum with variants `Enabled` and `Disabled`; it has custom deserialization that treats the empty string as enabled. `GroupAddRemove` contains group name, member list, `groupStatus`, and `isRemove` fields. `GroupDesc` contains group name/status/members/policy and optional `updatedAt` timestamp serialized/deserialized as RFC3339 through `time::serde::rfc3339::option`.

Control flow: deserialization of `GroupStatus` reads a string and matches `""` or `"enabled"` to enabled, `"disabled"` to disabled, and rejects all other values. The rest is serde field mapping.

State and persistence behavior: these are plain DTOs with no persistence logic. `updated_at` is optional and skipped on serialization when absent. Using `OffsetDateTime` preserves timezone-offset-aware timestamps in admin JSON.

Dependencies and integration points: depends on `serde` and `time`. These structures likely back madmin group add/remove/describe APIs and must match MinIO-compatible field names (`groupStatus`, `isRemove`, `updatedAt`).

Risks: `GroupDesc.status` is a raw `String`, not `GroupStatus`, so invalid statuses can be represented and serialized. `GroupStatus` custom deserializer is intentionally lenient for empty strings, but only lowercase accepted strings are supported. Timestamp serialization removes nanoseconds in the test setup but the serde helper can encode full RFC3339 values.

Test signals: tests verify `updatedAt` RFC3339 round-trip and empty-string status deserializing to enabled. Additional tests should cover invalid status rejection and field renames for `GroupAddRemove`.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/madmin/src/group.rs -->
