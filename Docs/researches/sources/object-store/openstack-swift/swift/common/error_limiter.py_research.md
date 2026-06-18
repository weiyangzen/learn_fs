# sources/object-store/openstack-swift/swift/common/error_limiter.py

Purpose: tracks recent backend node errors and suppresses use of nodes that exceed a configured error count for a configured interval.

Important APIs/types/functions: `ErrorLimiter` stores `suppression_interval`, `suppression_limit`, and a `stats` mapping keyed by `node_to_string`. `is_limited` reports and expires suppression state, `limit` immediately forces a node over the threshold, and `increment` records one error and reports whether the threshold is exceeded.

Control flow: `increment` and `limit` update `errors` and `last_error` for a node. `is_limited` returns false if no errors exist, removes stale entries when the last error is older than the interval, and otherwise checks `errors > suppression_limit`.

State and persistence: all state is in-memory per process; suppression resets on process restart. The map can grow with distinct nodes until entries are checked and expired.

Dependencies and integration: depends on `time.time` and Swift `node_to_string`. Used by proxy/backend selection code to avoid repeatedly selecting unhealthy storage nodes.

Risks: no locking is used, so concurrent green threads share mutable dictionaries cooperatively; stale entries only disappear when checked; threshold is strictly greater than the limit, so a limit of N allows N errors and suppresses on N+1; key stability depends on `node_to_string`. Tests should cover threshold boundary, immediate limit, expiry cleanup, and node key normalization.
