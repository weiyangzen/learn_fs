# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/OzoneManagerVersion.java

## Purpose
`OzoneManagerVersion` enumerates server-side Ozone Manager protocol feature versions and maps protobuf integer values to enum constants for compatibility checks.

## Important APIs, types, and functions
- Enum values track OM features from `DEFAULT_VERSION` through `S3_BUCKET_TAGGING_API`, with `FUTURE_VERSION(-1)` for unknown newer server versions.
- `CURRENT` is the latest known concrete version.
- `description()` and `toProtoValue()` implement `ComponentVersion`.
- `fromProtoValue(int)` uses a static lookup map and defaults unknown values to `FUTURE_VERSION`.

## Control flow
Static initialization builds `BY_PROTO_VALUE`. `latest()` returns `values()[values.length - 2]`, intentionally selecting the enum before `FUTURE_VERSION`; this requires all real versions to appear before the sentinel.

## State and persistence behavior
State is static enum metadata. Version values are serialized externally in protocol messages; this class does not persist data itself.

## Dependencies and integration points
It implements `ComponentVersion` and is referenced by client compatibility requirements, including defaults in `OzoneConfigKeys`.

## Risks and edge cases
Adding new real versions after `FUTURE_VERSION` would break `CURRENT`. Duplicate integer values would break lookup semantics. Unknown older or malformed values map to `FUTURE_VERSION`, which callers should treat carefully.

## Test signals
Tests should verify `CURRENT` is `S3_BUCKET_TAGGING_API`, all known values round-trip, unknown values map to `FUTURE_VERSION`, and enum ordering constraints are enforced when new versions are added.
