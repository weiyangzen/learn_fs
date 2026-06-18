# sources/sync-backup/kopia/internal/server/api_error.go

Purpose: centralizes conversion of server handler failures into HTTP status and API error payloads.

Important APIs/types/functions: `apiError`, `requestError`, `unableToDecodeRequest`, `notFoundError`, `accessDeniedError`, `repositoryNotWritableError`, and `internalServerError`.

Control flow: helper constructors choose HTTP code, `serverapi.APIErrorCode`, and message. Request/decode errors are 400, not found is 404, access denied is 403, and internal errors are 500.

State and persistence behavior: stateless value construction.

Dependencies and integration points: all `apiRequestFunc` handlers return `*apiError` for the common response wrapper in `server.go`.

Risks and test signals: overuse of `internalServerError` can hide client-actionable errors. API tests should assert both HTTP status and structured error code.
