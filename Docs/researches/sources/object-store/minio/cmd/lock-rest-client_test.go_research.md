# sources/object-store/minio/cmd/lock-rest-client_test.go

## Purpose

`lock-rest-client_test.go` verifies that a remote lock client created for an unreachable endpoint reports offline state and surfaces errors for lock operations. It is a negative-path test for `lock-rest-client.go`.

## Important Test Flow

`TestLockRESTlient` creates one remote endpoint at `localhost:9876` and one local endpoint at `localhost:9012`, marks the second as local, and initializes the global lock grid with both. It constructs a `newlockRESTClient` for the unreachable remote endpoint, expects `IsOnline` to be false, and then attempts `RLock`, `Lock`, `RUnlock`, and `Unlock` with empty `dsync.LockArgs`, expecting each call to return an error.

The test depends on endpoint parsing, `initGlobalLockGrid`, grid connection state, and `dsync.LockArgs`.

## Risks And Test Signals

The test confirms failure propagation for disconnected clients but has a typo in the function name (`TestLockRESTlient`). It does not exercise `Refresh`, `ForceUnlock`, local endpoint selection through `newLockAPI`, response-code translation, or a live server. Its main signal is that calls should not silently succeed when the grid connection is unavailable.
