# sources/storage-engines/foundationdb/fdbrpc/HealthMonitor.cpp

`HealthMonitor.cpp` tracks recent peer connection closures and reports peers whose closure count exceeds the configured instability threshold.

The API is compact: `reportPeerClosed()` records a `(now(), NetworkAddress)` event and increments that peer's count; `purgeOutdatedHistory()` removes events older than `HEALTH_MONITOR_CLIENT_REQUEST_INTERVAL_SECS`; `tooManyConnectionsClosed()` checks whether the count is greater than `HEALTH_MONITOR_CONNECTION_MAX_CLOSED`; `closedConnectionsCount()` exposes the current count; and `getRecentClosedPeers()` returns addresses still present in the rolling window.

Control flow is deque-plus-map maintenance. Every read/write entry point purges stale entries first, preserving O(1) current count lookup while retaining time-ordered expiry.

State is in-memory only and belongs to the owning transport. Dependencies are `fdbrpc/HealthMonitor.h`, Flow time/knobs, and `NetworkAddress`. `FlowTransport` reports public connection closures and uses the threshold to mark unstable peers failed or later available through `IFailureMonitor`.

Risks are mostly threshold and window semantics: exactly the configured maximum is still allowed because the check is strict greater-than, and high churn can grow the deque until time advances enough to purge. There are no direct tests; indirect signals are `FlowTransport` health TraceEvents and connection-churn simulation behavior.
