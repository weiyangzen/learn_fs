# sources/object-store/minio/cmd/lock-rest-server-common.go

## Purpose

`lock-rest-server-common.go` defines the shared sentinel errors used by the grid lock server and client. These errors form the semantic bridge between local locker outcomes and `dsync.LockResp` response codes.

## Important APIs, Control Flow, And State

The file declares `errLockConflict`, `errLockNotInitialized`, and `errLockNotFound` as package-level `errors.New` values. `lock-rest-server.go` maps them to `dsync.RespLockConflict`, `dsync.RespLockNotInitialized`, and `dsync.RespLockNotFound`; `lock-rest-client.go` maps `RespLockNotInitialized` back to `errLockNotInitialized` and treats conflict/not-found as false replies without Go errors.

There is no mutable state or persistence. The dependency is only the standard `errors` package.

## Risks And Test Signals

Because server response mapping relies on direct error identity in a switch, wrapping these sentinel errors before `makeResp` would break classification. The common test file exercises lower-level lock entry removal, not the sentinel values directly. Response-code behavior is indirectly covered by lock client/server tests elsewhere.
