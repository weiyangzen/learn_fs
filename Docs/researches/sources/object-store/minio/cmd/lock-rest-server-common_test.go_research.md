# sources/object-store/minio/cmd/lock-rest-server-common_test.go

## Purpose

`lock-rest-server-common_test.go` provides test setup for a lock server and validates `localLocker.removeEntry`, the helper used by unlock and force-unlock paths. Despite the filename, the concrete assertion is about local lock entry deletion semantics.

## Important Tests And Control Flow

`createLockTestServer` prepares a filesystem-backed test object layer, initializes config, constructs a `lockRESTServer` with a `localLocker` containing a mutex and `lockMap`, authenticates node credentials, and returns the temp path, locker, and token. `TestLockRpcServerRemoveEntry` inserts two write-lock requester entries under `"name"`, verifies an unknown UID does not remove anything, removes the first UID and checks the remaining slice contains the second entry, then removes the second UID and expects the lock map entry to be nil.

Dependencies include `prepareFS`, `newTestConfig`, `globalActiveCred`, `authenticateNode`, `reflect.DeepEqual`, and `dsync.LockArgs`.

## Risks And Test Signals

The test confirms UID/owner matching and slice update behavior in `removeEntry`, but its hand-built locker omits `lockUID`, so it does not validate UID-index cleanup. It also does not exercise grid handlers, response-code mapping, token use, or concurrent access. Its setup helper can support broader server tests if expanded.
