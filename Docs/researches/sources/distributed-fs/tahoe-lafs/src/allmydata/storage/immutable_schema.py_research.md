# sources/distributed-fs/tahoe-lafs/src/allmydata/storage/immutable_schema.py

## Purpose
Defines versioned immutable share container schemas and header creation logic.

## Important APIs, Types, and Functions
`_Schema` stores a version number and lease serializer, and `header(max_size)` builds the 12-byte immutable share header. Module constants are `ALL_SCHEMAS`, `ALL_SCHEMA_VERSIONS`, and `NEWEST_SCHEMA_VERSION`. `schema_from_version(version)` resolves a schema object.

## Control Flow
On import, schemas for immutable versions 1 and 2 are built from lease-schema serializers. `header()` packs version, capped 32-bit share size, and zero initial lease count. `schema_from_version()` linearly searches known schemas.

## State and Persistence Behavior
No runtime state beyond constants. The header format directly determines persisted immutable share-file metadata. The size field is saturated at `2**32 - 1` for downgrade compatibility.

## Dependencies and Integration Points
Used by `ShareFile` to write new containers and decode existing versions. Depends on `.lease_schema.v1_immutable` and `.lease_schema.v2_immutable`.

## Risks and Edge Cases
The schema set is unordered, though newest is computed by max version. Unknown versions return `None` and are translated by `ShareFile` into `UnknownImmutableContainerVersionError`.

## Test Signals
`test_storage.py` property tests sample all immutable schemas for read/write, bounds, lease overflow, and secret behavior. Bad-version storage tests exercise lookup failure.
