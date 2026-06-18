<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/grid.go -->
# sources/object-store/minio/cmd/grid.go

## Purpose
Initializes global persistent websocket grid managers for internode RPC and distributed lock traffic. It creates separate managers for storage/admin grid routes and lock-grid routes.

## Important APIs, types, and functions
- `globalGrid` and `globalLockGrid` are atomic pointers to `grid.Manager`.
- `globalGridStart` and `globalLockGridStart` are startup gates for grid connections.
- `initGlobalGrid` creates the main grid manager with `grid.RoutePath`.
- `initGlobalLockGrid` creates the lock grid manager with `grid.RouteLockPath`.

## Control flow
Each initializer derives hosts and local node from endpoint pools, uses DNS-cache-backed internode dialers configured for websockets, sets TLS roots/ciphers/curves, provides cached auth tokens and validation callbacks, wires byte counters and trace output, and stores the resulting manager atomically. The lock initializer uses the lock route path in its websocket connector and manager options.

## State and persistence behavior
No durable state. Runtime state is the globally stored manager and startup gate channels. Incoming/outgoing counters mutate global connection stats.

## Dependencies and integration points
Depends on endpoint pools, DNS cache, internode HTTP dialer/TCP options, MinIO crypto TLS policy, storage request token validation, cached auth tokens, global trace pubsub, and MinIO grid package.

## Risks and edge cases
Internode connectivity depends on correct endpoint host discovery, DNS resolution, TLS roots, route path, and auth token validation. Both managers use `globalGridStart` as the block channel in the shown code; if the separate lock gate is expected, this may be intentional coupling or a subtle configuration risk.

## Test signals
No direct tests here. Signals come from distributed startup, internode RPC, lock acquisition, byte counters, and grid route health under TLS and DNS changes.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/grid.go -->
