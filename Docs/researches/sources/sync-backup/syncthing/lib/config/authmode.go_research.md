# sources/sync-backup/syncthing/lib/config/authmode.go

Purpose: Text-marshaled enum for GUI authentication mode.

Important APIs/types/functions: `AuthMode` has `AuthModeStatic` and `AuthModeLDAP`. `String`, `MarshalText`, and `UnmarshalText` convert between enum values and `static`/`ldap`.

Control flow: `UnmarshalText` defaults unknown values to static and returns nil.

State and persistence behavior: Used in config XML/JSON text representation. Defaulting unknown values to static preserves a conservative local-auth fallback.

Dependencies and integration points: Consumed by API auth logic, specifically `auth` in `api_auth.go`, and by config serialization.

Risks: Unknown config values silently become static, which may hide typos. Adding new modes requires updating string conversion and auth dispatch.

Test signals: No direct test in this subset. Auth tests exercise the static path.
