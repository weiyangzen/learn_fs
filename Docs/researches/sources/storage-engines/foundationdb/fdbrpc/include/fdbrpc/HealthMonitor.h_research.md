# sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/HealthMonitor.h

## Purpose
`HealthMonitor.h` declares a small peer health tracker that records recently closed connections and flags peers with too many closures.

## Important APIs, Types, and Functions
`HealthMonitor` exposes `reportPeerClosed`, `tooManyConnectionsClosed`, `closedConnectionsCount`, and `getRecentClosedPeers`. Private state is maintained by `purgeOutdatedHistory`, `peerClosedHistory`, and `peerClosedNum`.

## Control Flow
Callers report a closed peer address. Query methods purge outdated history, count recent closures, and return either a threshold decision, a per-peer count, or the set of peers with recent closures.

## State and Persistence Behavior
State is in-memory: a deque of timestamp/address pairs and a map of address to recent close count. No state persists across process restart.

## Dependencies and Integration Points
It depends on Flow time/network address types and standard containers. `FlowTransport` exposes a `healthMonitor()` accessor and likely uses this to inform connection health/degradation logic.

## Risks and Edge Cases
The thresholds and history window are hidden in implementation, so callers must treat results as heuristic. The data structure is not inherently thread-safe. If purge is only called on queries, inactive monitors can retain stale history until queried.

## Test Signals
Tests should report repeated closes for one peer, verify count and threshold behavior, then advance time or purge to confirm old entries expire.
