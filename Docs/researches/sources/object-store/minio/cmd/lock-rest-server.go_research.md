# sources/object-store/minio/cmd/lock-rest-server.go

## Purpose

`lock-rest-server.go` exposes the local lock manager over MinIO's grid RPC system. It registers typed lock handlers, translates local locker results into `dsync.LockResp` codes, and starts background maintenance for distributed erasure deployments.

## Important APIs, Control Flow, And State

`lockRESTServer` wraps a `*localLocker`. Handler methods are thin adapters: `RefreshHandler` uses `dsync.DefaultTimeouts.RefreshCall` and returns not-found when refresh fails without error; `LockHandler` and `RLockHandler` use acquire timeouts and translate false success to `errLockConflict`; `UnlockHandler`, `RUnlockHandler`, and `ForceUnlockHandler` call the local locker with background context and ignore boolean replies when errors communicate failure. Global handlers (`lockRPCForceUnlock`, `lockRPCRefresh`, `lockRPCLock`, `lockRPCUnlock`, `lockRPCRLock`, `lockRPCRUnlock`) are created with `newLockHandler`.

`registerLockRESTHandlers` creates a new local locker, registers each handler with the grid manager using `logger.FatalIf`, stores it in `globalLockServer`, and launches `lockMaintenance(GlobalContext)`. `makeResp` maps nil and sentinel errors to `dsync.LockResp` codes and arbitrary errors to `RespErr` with a string. `lockMaintenance` only runs for distributed erasure, ticking once per minute and expiring locks older than `lockValidityDuration`.

State is the process-local `globalLockServer` and its in-memory lock maps. Integration points are grid manager registration, dsync timeout constants, and local locker expiration.

## Risks And Test Signals

Risks include response-code drift with clients, identity-based sentinel matching, background maintenance not running outside distributed erasure, and using background contexts for unlock paths. Tests in this subset cover local removal and offline clients, but not live grid handler round-trips or maintenance ticks.
