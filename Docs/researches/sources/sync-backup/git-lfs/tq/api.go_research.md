# sources/sync-backup/git-lfs/tq/api.go

Purpose: Git LFS batch API request/response types and HTTP client adapter.

Important APIs/types/functions: `tqClient`, `batchRef`, `batchRequest`, `BatchResponse`, `Batch`, `BatchClient`, and `tqClient.Batch`.

Control flow: `Batch` upgrades the manifest and sends operation, objects, adapter names, ref, and hash algorithm. `tqClient.Batch` omits `transfers` when only basic is requested, builds a POST to `objects/batch`, executes with auth/retries, decodes JSON, rejects unsupported hash algorithms, checks HTTP 200, and timestamps action creation times.

State and persistence: stores max retry count on `tqClient`; no durable state.

Dependencies and integration points: called by `TransferQueue`; schema tests validate request/response JSON. Integrates with `lfsapi.Client`, `lfshttp.Endpoint`, and remote refs.

Risks: `Batch` calls `remoteRef.Refspec()` without a nil guard. Non-200 responses are checked after JSON decode, so malformed error bodies surface as decode errors first.

Test signals: `api_test.go` covers normal request/response, basic-only transfer omission, empty object short-circuit, and JSON schema validation.
