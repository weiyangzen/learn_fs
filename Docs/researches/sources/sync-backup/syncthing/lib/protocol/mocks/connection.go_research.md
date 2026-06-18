# sources/sync-backup/syncthing/lib/protocol/mocks/connection.go

## Purpose
Generated external-package fake for the full `protocol.Connection` interface. It supports tests outside the `protocol` package that need to stub connection behavior, observe method calls, and assert interactions without opening a real BEP connection.

## Important APIs, Types, and Functions
`Connection` has generated fake surfaces for connection operations (`Start`, `Close`, `Closed`, `Index`, `IndexUpdate`, `Request`, `ClusterConfig`, `DownloadProgress`), identity/statistics (`DeviceID`, `Statistics`), and embedded `ConnectionInfo` methods (`Type`, `Transport`, `IsLocal`, `RemoteAddr`, `Priority`, `String`, `Crypto`, `EstablishedAt`, `ConnectionID`). Argument inspectors such as `IndexArgsForCall`, return configurators, stubs, call counters, `Invocations`, and `recordInvocation` make up the testing API. The file ends with `var _ protocol.Connection = new(Connection)`.

## Control Flow
Every generated method follows the counterfeiter pattern: lock its mutex, append arguments to a call slice, capture the current stub and returns, record the invocation, unlock, then call the stub or return configured values. Methods returning errors or data use default return structs unless a per-call override exists. Void methods such as `Close` and `ClusterConfig` invoke the stub if configured.

## State and Persistence Behavior
The fake stores all state in memory behind per-method locks and a global invocation lock. Argument values are stored as provided, so pointer and map arguments remain shared with the caller. There is no durable state or network side effect unless a test-supplied stub performs one.

## Dependencies and Integration Points
Imports `context`, `net`, `sync`, `time`, and `github.com/syncthing/syncthing/lib/protocol`. It integrates with higher-level packages that accept `protocol.Connection`, especially model, folder, and request-path tests that need to simulate peer requests or assert emitted messages.

## Risks and Edge Cases
Generated mocks can hide protocol ordering and goroutine semantics because they do not implement real asynchronous writer/reader behavior. Pointer arguments are not deep-copied, so later mutation can affect assertions. Interface drift requires regeneration; the compile-time assertion catches missing methods.

## Test Signals
The compile-time assertion verifies interface coverage. Downstream tests should verify call counts, arguments, configured errors, and channel-return behavior for `Closed`; this file itself has no direct unit tests because it is generated support code.
