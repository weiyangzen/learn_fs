# sources/sync-backup/git-lfs/locking/api_test.go

Purpose: Tests HTTP locking API request/response shapes against JSON schemas.

Important APIs/types/functions: Exercises `httpLockClient.Lock`, `Unlock`, `Search`, `SearchVerifiable`, schema loaders, and `assertSchema`.

Control flow: Test servers assert path, method, headers, body content, and query parameters. Responses are encoded through schema writer loaders and decoded by the client. Schema fixtures are loaded during package init from `schemas/*.json`.

State and persistence behavior: Uses in-memory test servers and schema objects. No remote state persists beyond request counters implicit in handlers.

Dependencies and integration points: Integrates locking API with `lfsapi.NewClient`, `lfshttp.NewContext`, `gojsonschema`, and Git ref formatting.

Risks and edge cases: Schema load failures are printed during init and produce nil schema assertions if not guarded. Tests cover happy paths but not auth errors, conflict responses, invalid server responses, or non-200 search behavior.

Test signals: Strong contract signal for wire format and headers: `Accept`, `Content-Type`, and JSON payload structure.
