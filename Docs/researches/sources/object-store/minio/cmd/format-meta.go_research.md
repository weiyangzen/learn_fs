<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/format-meta.go -->
# sources/object-store/minio/cmd/format-meta.go

## Purpose
Defines the common top-level metadata embedded by backend-specific `format.json` schemas. It provides the shared version, backend format, and deployment ID fields used by erasure format code.

## Important APIs, types, and functions
- `formatConfigFile` names the persisted metadata file: `format.json`.
- `formatMetaVersionV1` is the current top-level metadata schema version.
- `formatMetaV1` contains JSON fields `version`, `format`, and `id`.

## Control flow
There is no executable control flow. Backend-specific structs embed `formatMetaV1` and add a backend object such as `xl`.

## State and persistence behavior
The struct represents on-disk `.minio.sys/format.json` state. `Version` guards schema compatibility, `Format` selects backend implementation, and `ID` is the deployment identifier used by hashing, replication, and operational identity.

## Dependencies and integration points
Used by `format-erasure.go` and other backend format files. Startup, migration, heal format generation, and `fmt-gen` all rely on these fields.

## Risks and edge cases
Changing this schema would require migration across all backend format implementations. Incorrect deployment ID preservation can affect object placement and replication identity.

## Test signals
Tests in `format-erasure_test.go` indirectly validate `Version`, `Format`, and `ID` behavior during migration, validation, quorum selection, and heal-format creation.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/format-meta.go -->
