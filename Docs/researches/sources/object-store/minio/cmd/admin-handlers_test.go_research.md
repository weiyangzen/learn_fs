# sources/object-store/minio/cmd/admin-handlers_test.go

## Purpose
`admin-handlers_test.go` provides unit and lightweight integration coverage for selected admin handler paths. It builds an in-process single-node erasure backend, registers the admin router, signs admin requests, and verifies service control, server info, admin error mapping, heal parameter parsing, and distributed-lock aggregation.

## Important APIs, Types, And Functions
- `adminErasureTestBed` captures temporary erasure disk paths, the initialized `ObjectLayer`, admin router, and a cancellation function.
- `prepareAdminErasureTestBed` resets globals, enables erasure mode, initializes an erasure object layer and test config, sets boot time/endpoints, initializes subsystems, starts IAM, and registers admin routes with config operations enabled.
- `TearDown` cancels the context, removes temporary disks, and resets globals.
- `initTestErasureObjLayer` creates sixteen random disks, builds erasure server pools, and publishes `globalObjectAPI`.
- `cmdType`, `restartCmd`, `stopCmd`, `toServiceSignal`, and `toServiceAction` map test commands to internal service signals and `madmin.ServiceAction`s.
- `getServiceCmdRequest` and `buildAdminRequest` construct signed V4 admin requests.
- Tests include `TestServiceRestartHandler`, `TestAdminServerInfo`, `TestToAdminAPIErrCode`, `TestExtractHealInitParams`, and `TestTopLockEntries`.

## Control Flow
The shared test setup is explicit and global-state-heavy. Each integration-style test creates a context, calls `prepareAdminErasureTestBed`, sets `globalMinioAddr` for admin peer behavior, builds a signed request against `adminPathPrefix + adminAPIVersionPrefix`, runs it through the registered mux router, checks HTTP status, and decodes JSON where needed. Service restart starts a goroutine that reads from `globalServiceSignalCh` and compares the internal signal with the expected value.

`TestExtractHealInitParams` does combinatorial validation over query parameter combinations and route-variable combinations. It expects invalid cases when both force flags are present, when a client token is mixed with force flags, or when a prefix is given without a bucket. The body is fixed valid JSON, so JSON parser failures are intentionally not tested.

`TestTopLockEntries` constructs synthetic lock requester info for grouped delete-object locks and concurrent read locks across four owners. It creates identical `PeerLocks` maps per owner, builds expected `madmin.LockEntry` values, calls `topLockEntries`, sorts expected and actual by resource/UID, and compares fields except elapsed time.

## State And Persistence Behavior
Tests create and delete temporary erasure disk directories and mutate numerous MinIO globals (`globalIsErasure`, `globalObjectAPI`, `globalEndpoints`, `globalBootTime`, IAM/config subsystems, `globalMinioAddr`). `TearDown` is required to clean disks and restore globals. The service restart test reads from the global service signal channel but only starts a receiver for restart; stop command helpers exist but are not currently exercised.

## Dependencies And Integration Points
The file relies on test helpers from the broader MinIO `cmd` package: `resetTestGlobals`, `getRandomDisks`, `mustGetPoolEndpoints`, `newErasureServerPools`, `newTestConfig`, subsystem initialization functions, `newTestRequest`, and `signRequestV4`. It integrates with `madmin-go/v3`, `internal/auth`, `mux`, the admin router, IAM policy setup, and erasure object-layer internals.

## Risks And Edge Cases
Because tests mutate package globals, ordering and cleanup discipline matter. Missing `TearDown` or early failures before defers could leak temporary state into later tests. The service restart test can block if the handler does not send the expected signal; it uses a `WaitGroup` without timeout. The lock aggregation test constructs each peer with the full lock map, which verifies aggregation/quorum behavior under a synthetic model but may not reflect divergent peer lock views.

Coverage is selective. It does not test dry-run service behavior, stop handling, update handling, freeze/unfreeze, streaming handlers, KMS, inspect data, health anonymization, metrics, or most peer-failure paths. `TestExtractHealInitParams` assumes the body is valid and therefore does not cover `ErrRequestBodyParse`.

## Test Signals
The file itself is the test signal for `admin-handlers.go` and `admin-heal-ops.go`. It confirms that a registered admin route can authenticate and return server info in a single-node erasure setup, that restart command signaling reaches `globalServiceSignalCh`, that `toAdminAPIErrCode` maps quorum errors specially, that heal initialization rejects conflicting token/force combinations and invalid prefix-without-bucket paths, and that `topLockEntries` preserves key lock fields while aggregating server lists.
