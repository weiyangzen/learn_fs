## sources/sync-backup/kopia/internal/acl/access_level.go

Purpose: defines ACL access-level enumeration and JSON/string conversion.

Important APIs/types/functions: `AccessLevel`, constants `AccessLevelNone`, `AccessLevelRead`, `AccessLevelAppend`, `AccessLevelFull`, `SupportedAccessLevels`, `ParseAccessLevel`, `MarshalJSON`, `UnmarshalJSON`, and `String`.

Control flow, state, and persistence: access levels are integers persisted as JSON strings (`NONE`, `READ`, `APPEND`, `FULL`). Reverse lookup is built in `init`. Unknown marshal values fail; unknown unmarshal strings silently map to zero because map lookup is unchecked.

Dependencies and integration points: used by `acl.Entry`, auth authorization aliases, and repository ACL manifests.

Risks and test signals: silent unknown-string unmarshal can produce invalid zero values that later `Validate` should reject, but direct JSON callers may need care. Tests cover valid JSON serialization round trip.
