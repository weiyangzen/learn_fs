# sources/sync-backup/git-lfs/tq/schemas/http-batch-request-schema.json

Purpose: JSON Schema draft-04 contract for Git LFS HTTPS batch API requests.

Important APIs/types/functions: schema fields `transfers`, `operation`, and `objects`; object entries require `oid` and nonnegative numeric `size`, with optional `authenticated`.

Control flow: not executable; consumed by tests through gojsonschema.

State and persistence: static schema file.

Dependencies and integration points: `api_test.go` validates generated `batchRequest` JSON against this schema.

Risks: schema omits newer fields present in Go structs such as `ref` and `hash_algo`, so additional request properties at top level are not rejected because top-level `additionalProperties` is not false.

Test signals: loaded by `TestAPIBatch` and `TestAPIBatchOnlyBasic`.
