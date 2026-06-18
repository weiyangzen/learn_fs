# sources/sync-backup/git-lfs/locking/api.go

Purpose: Implements Git LFS locking API clients for HTTP and dispatch to pure SSH lock transfer when available.

Important APIs/types/functions: `lockClient`, `httpLockClient`, `lockRequest`, `lockResponse`, `unlockRequest`, `unlockResponse`, `lockSearchRequest.QueryValues`, `lockList`, `lockVerifiableRequest`, `lockVerifiableList`, `User`, `genericLockClient`, and lock methods `Lock`, `Unlock`, `Search`, `SearchVerifiable`.

Control flow: HTTP methods choose upload/download endpoints, build requests with `lfsapi.Client.NewRequest`, log request keys, execute through `DoAPIRequestWithAuth`, decode JSON on success, and return response/status/error. `genericLockClient` memoizes per remote/operation client, choosing SSH lock client if `Client.SSHTransfer` succeeds, otherwise HTTP.

State and persistence behavior: No lock persistence here beyond remote API effects. `genericLockClient` caches selected lock clients in memory. `SetAccess`/auth side effects happen in `lfsapi`.

Dependencies and integration points: Integrates `lfsapi.Client`, `lfshttp.DecodeJSON`, Git refs, locking schema types, and pure SSH lock client implementation outside this file.

Risks and edge cases: `Unlock` always dereferences `ref.Refspec()`, so callers must pass a non-nil ref. Lock/unlock require either a lock object or server message; otherwise response is invalid. Search only decodes JSON on HTTP 200, preserving status for non-OK responses.

Test signals: `api_test.go` covers request shape, JSON schemas, status propagation, query parameters, and response decoding for HTTP paths.
