## sources/sync-backup/kopia/internal/acl/access_level_test.go

Purpose: validates JSON serialization for all supported ACL access levels.

Important APIs/types/functions: `TestAccessLevelJSONSerialization`.

Control flow, state, and persistence: creates a struct containing each access level, marshals with indentation, compares exact JSON strings, then unmarshals and compares the struct.

Dependencies and integration points: exercises Go JSON integration for repository ACL manifests.

Risks and test signals: confirms only the valid happy path. It does not test unsupported strings or invalid numeric values, leaving error-path coverage to validation tests.
