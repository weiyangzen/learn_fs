# sources/object-store/minio/cmd/peer-rest-client.go

## Purpose
This file implements the client side of MinIO internode peer operations. It wraps legacy REST endpoints and newer grid RPC/stream handlers for health, admin state, IAM reloads, bucket metadata, metrics, tracing, console logs, rebalance, binary updates, and performance diagnostics.

## Important APIs, Types, and Functions
`peerRESTClient` holds a peer host, `rest.Client`, grid host, and lazy grid connection lookup. `newPeerRESTClient` builds authenticated HTTP clients and a health check. `callWithContext` normalizes network failures to `errPeerNotReachable`. Many methods call typed grid handlers: `GetLocks`, `LocalStorageInfo`, `ServerInfo`, `GetMetrics`, IAM reload/delete functions, metacache functions, rebalance/tier reload functions, bandwidth and metrics methods. Legacy HTTP/gob methods include profiling, binary verify/commit, speed tests, drive speed tests, dev-null, netperf, and replication MRF streaming.

## Control Flow and State
Grid connections are cached in an atomic pointer after `globalGrid` becomes available. Streaming APIs start goroutines that reconnect every five seconds until context cancellation and drop data when downstream channels are full.

## Dependencies and Integration Points
The client depends on `peer-rest-common.go` constants, grid handlers registered by `peer-rest-server.go`, global internode transport/auth, madmin types, and notification/admin systems that fan out calls across `globalNotificationSys`.

## Risks and Test Signals
Nil or unavailable grid connections often return nil/no-op for best-effort reload calls, so callers must tolerate eventual consistency. Streaming backpressure drops trace/log/listen messages. Legacy HTTP paths need body draining to preserve connections. This subset has no direct client tests; server registration and higher-level admin tests are the likely coverage.
