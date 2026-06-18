# sources/sync-backup/git-lfs/tq/schemas/http-batch-response-schema.json

Purpose: JSON Schema draft-04 contract for Git LFS HTTPS batch API responses.

Important APIs/types/functions: defines action objects with `href`, headers, expiration fields; response fields `transfer`, `objects`, error object, `message`, `request_id`, and `documentation_url`; each object requires `oid` and nonnegative `size`.

Control flow: static validation schema only.

State and persistence: static file.

Dependencies and integration points: used by `api_test.go` to validate test server responses.

Risks: action `additionalProperties: false` means extensions to action payloads require schema updates. Top-level response allows additional fields unless constrained elsewhere.

Test signals: loaded by API schema tests.
