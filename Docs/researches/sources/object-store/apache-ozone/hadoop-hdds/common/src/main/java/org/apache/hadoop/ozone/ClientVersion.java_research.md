# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/ClientVersion.java

## Purpose
`ClientVersion` enumerates protocol client feature versions and maps integer protobuf values to semantic version constants. It lets servers and clients reason about compatibility and feature availability.

## Important APIs, types, and functions
- Enum values include `DEFAULT_VERSION`, `VERSION_HANDLES_UNKNOWN_DN_PORTS`, `ERASURE_CODING_SUPPORT`, `BUCKET_LAYOUT_SUPPORT`, and `FUTURE_VERSION`.
- `CURRENT` and `CURRENT_VERSION` represent the latest known nonnegative version.
- `description()` and `toProtoValue()` implement `ComponentVersion`.
- `fromProtoValue(int)` maps wire values to enum constants, defaulting to `FUTURE_VERSION`.

## Control flow
Static initialization builds `BY_PROTO_VALUE` from enum values and computes `CURRENT` via maximum protobuf value. Unknown future positive values and any unrecognized integer map to `FUTURE_VERSION`.

## State and persistence behavior
State is static immutable enum metadata and a static lookup map. Version integers are persisted externally in protocol messages, not by this class.

## Dependencies and integration points
It implements `org.apache.hadoop.hdds.ComponentVersion` and is used by client/server protocol negotiation and feature gates.

## Risks and edge cases
`latest()` uses max `toProtoValue`, so `FUTURE_VERSION(-1)` is safely excluded while current versions remain nonnegative. Adding a new version must preserve unique integer values. Unknown negative values also map to `FUTURE_VERSION`, which may or may not match caller expectations.

## Test signals
Tests should verify current version, round-trip for each enum integer, unknown value mapping, and that new enum additions update `CURRENT_VERSION`.
