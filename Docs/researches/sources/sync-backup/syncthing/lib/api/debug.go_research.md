# sources/sync-backup/syncthing/lib/api/debug.go

Purpose: API package debug logger registration and HTTP debug-level predicate.

Important APIs/types/functions: Package variable `l` is a `slogutil` adapter registered as "REST API". `shouldDebugHTTP` returns whether package `api` is set to debug level.

Control flow: `shouldDebugHTTP` delegates to `l.ShouldDebug("api")`.

State and persistence behavior: Registers API package metadata in global slogutil state. No persistence.

Dependencies and integration points: Used by `debugMiddleware` and server error-log configuration in `api.go`, plus debug logs in auth/CSRF/statics/config code.

Risks: The explicit `"api"` facility string must match `funcNameToPkg` package derivation. If package names change, debug toggles could stop matching.

Test signals: API log-level endpoint and debug behavior are indirectly covered by API tests.
