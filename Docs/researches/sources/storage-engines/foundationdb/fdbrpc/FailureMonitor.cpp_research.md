# sources/storage-engines/foundationdb/fdbrpc/FailureMonitor.cpp

## Purpose
`FailureMonitor.cpp` implements helper waits for endpoint failure state and the simple in-memory failure monitor used by Flow transport to track address health, permanently failed endpoints, unauthorized endpoint access, and disconnect notifications.

## Important APIs, Types, and Functions
Important functions include `waitForStateEqual`, `waitForContinuousFailure`, `IFailureMonitor::onStateEqual`, and `IFailureMonitor::onFailedFor`. `SimpleFailureMonitor` implements `setStatus`, `endpointNotFound`, `unauthorizedEndpoint`, `notifyDisconnect`, `onDisconnectOrFailure`, `onDisconnect`, `onStateChanged`, `getState` overloads, `onlyEndpointFailed`, `permanentlyFailed`, `knownUnauthorized`, and `reset`.

## Control Flow
Wait helpers subscribe to monitor change futures, check current state, and loop until the requested state or sustained-failure condition is met. `SimpleFailureMonitor::setStatus` updates the address-status map and triggers endpoint ranges when address health changes. Endpoint-not-found and unauthorized paths record permanent endpoint failure and trigger that endpoint. Disconnect notification triggers all endpoints on the address plus address-level disconnect watchers. Query methods combine permanent endpoint failures with address status.

## State and Persistence Behavior
State is process-local and in memory: `addressStatus`, `failedEndpoints`, `endpointKnownFailed`, and `disconnectTriggers`. The constructor marks local primary and secondary addresses healthy. `failedEndpoints` can grow for public endpoints; a safety clear occurs after 100000 entries. `reset` clears maps and trigger state.

## Dependencies and Integration Points
It depends on `fdbrpc/FailureMonitor.h`, Flow transport local addresses, network knobs, `AsyncMap`-style triggers, `Endpoint`, `NetworkAddress`, `UID`, and trace events. It is a core integration point for RPC failure handling and load balancing.

## Risks and Edge Cases
`endpointNotFound` comments that permanent endpoint state can leak memory. Well-known endpoint-not-found is logged but not permanently marked. `onStateChanged` returns `Never()` for permanently failed endpoints because their state cannot change, so callers must check state before waiting. Sustained failure wait uses a slope formula and timeout polling rather than only change notifications. Public endpoint failure map clearing loses diagnostic memory to cap growth.

## Test Signals
Flow tests in this subset exercise `waitValueOrSignal` behavior around peer disconnect and retry. Broader transport tests should validate address status changes, unauthorized endpoints, disconnect triggers, and sustained failure waits.
