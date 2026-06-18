# sources/object-store/minio/cmd/lock-rest-client.go

## Purpose

`lock-rest-client.go` implements the remote `dsync.NetLocker` client over MinIO's grid RPC layer. It forwards distributed lock operations to a remote lock server and translates `dsync.LockResp` codes into boolean success and Go errors.

## Important APIs, Control Flow, And State

`lockRESTClient` holds a `*grid.Connection`. `IsOnline` reports whether the connection state is `grid.StateConnected`; `IsLocal` is false; `String` returns the remote address; `Close` is a no-op. The shared `call` method invokes a typed `grid.SingleHandler[*dsync.LockArgs,*dsync.LockResp]`, returns `ok` when the response code is `dsync.RespOK`, maps `RespLockConflict`, `RespLockNotFound`, and `RespOK` to no error, maps `RespLockNotInitialized` to `errLockNotInitialized`, and maps other response errors to `errors.New(r.Err)`.

`RLock`, `Lock`, `RUnlock`, `Refresh`, `Unlock`, and `ForceUnlock` are thin wrappers selecting the corresponding global handler. `newLockAPI` returns `globalLockServer` for local endpoints and a new REST client for remote endpoints. `newlockRESTClient` obtains the grid connection from `globalLockGrid` using `Endpoint.GridHost()`.

State is the connection object; lock persistence is on the remote local locker. Dependencies are `internal/dsync`, `internal/grid`, endpoint metadata, and global lock-grid initialization.

## Risks And Test Signals

Risks include stale connection state, response-code compatibility between client and server, and treating lock conflict/not-found as non-error while relying on the boolean. `lock-rest-client_test.go` covers an offline endpoint and verifies all basic lock calls fail with connection errors. It does not cover a successful connected server or every response-code mapping.
