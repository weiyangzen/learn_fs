# sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/FailureMonitor.h

## Purpose
`FailureMonitor.h` defines the failure-monitoring abstraction used by FoundationDB components to track unavailable addresses, missing endpoints, unauthorized endpoints, disconnects, and wait conditions for failure state changes.

## Important APIs, Types, and Functions
`FailureStatus` wraps a failed/available boolean and serializes it. `IFailureMonitor` declares state queries for endpoints and addresses, endpoint failure notifications, unauthorized notification, state-change futures, disconnect futures, permanent/endpoint-only/unauthorized checks, `notifyDisconnect`, `setStatus`, `onStateEqual`, `onFailed`, `onFailedFor`, and static `failureMonitor`. `SimpleFailureMonitor` implements the interface with address maps, endpoint maps, and async triggers.

## Control Flow
Transport and clients call `setStatus`, `endpointNotFound`, `unauthorizedEndpoint`, and `notifyDisconnect` as network events occur. Callers query current state or wait for futures such as `onStateChanged`, `onDisconnectOrFailure`, and `onFailedFor` before retrying or reconfiguring. New endpoints on healthy addresses are treated optimistically unless endpoint-specific failure is known.

## State and Persistence Behavior
State is process-local: address statuses, endpoint-known-failed async map, disconnect triggers, and endpoint failure reasons. It is resettable and not durable.

## Dependencies and Integration Points
It depends on Flow futures/maps, `FlowTransport.h` for `Endpoint`, and network globals. It integrates directly with `FlowTransport`, load balancing, data distribution, and callers using `g_network->failureMonitor()`.

## Risks and Edge Cases
The monitor is intentionally local and reactive, not an active failure detector. It can report temporary false failures or optimistic availability. Endpoint failures and address failures have different semantics, so callers must distinguish `onlyEndpointFailed` from full address failure. Future behavior depends on implementation in the companion source.

## Test Signals
Tests should cover address status transitions, endpoint-not-found behavior, unauthorized endpoints, disconnect triggers, `onFailedFor` timing, and reset behavior. Transport tests that close connections provide integration signals.
