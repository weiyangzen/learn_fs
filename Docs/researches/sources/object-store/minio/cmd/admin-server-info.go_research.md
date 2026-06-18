# sources/object-store/minio/cmd/admin-server-info.go

## Purpose
`admin-server-info.go` builds the local node portion of MinIO admin server information. It collects endpoint identity, pool membership, peer reachability, process/runtime memory and GC stats, redacted MinIO environment variables, and local disk state for inclusion in `madmin.ServerProperties`.

## Important APIs, Types, And Functions
- `getLocalServerProperty(endpointServerPools EndpointServerPools, r *http.Request, metrics bool) madmin.ServerProperties` is the file's sole function.
- It uses endpoint pool topology to determine local pool numbers and network status.
- It reads Go runtime memory and GC stats, truncating GC pause slices to at most five entries.
- It redacts sensitive MinIO environment variables before adding them to the response.
- It obtains local storage info from the object layer when initialized, otherwise returns offline disk placeholders.

## Control Flow
The function selects an address from `globalLocalNodeName`, `r.Host`, or distributed-erasure global state. It walks all endpoints. Local endpoints add pool numbers and are marked online in the network map. Remote endpoints are checked once per host with `isServerResolvable` and classified online, offline, or timed out based on network error helpers.

After network collection, it reads `runtime.MemStats` and `debug.GCStats`, constructs `madmin.ServerProperties`, sorts pool numbers, and sets `PoolNumber` only when exactly one pool is local; otherwise it uses `math.MaxInt` to indicate unset/multiple. It scans `os.Environ`, keeps only `MINIO` and `_MINIO` variables, and redacts known credentials plus variables containing `password` or ending in `key`. Finally, it reads local object-layer storage info with the requested metrics flag or returns initializing/offline disk state if the object layer is unavailable.

## State And Persistence Behavior
The function is read-only. It observes globals, endpoint reachability, environment variables, runtime process stats, and object-layer storage state. It does not mutate persistent storage or global state.

## Dependencies And Integration Points
This function is called by `getServerInfo` in `admin-handlers.go`. It depends on endpoint types, `globalLocalNodeName`, `globalIsDistErasure`, `globalBootTime`, build metadata (`Version`, `CommitID`), `newObjectLayerFn`, `getOfflineDisks`, `globalEndpoints`, MinIO config/KMS environment variable names, and `madmin-go/v3` response types.

## Risks And Edge Cases
Network status depends on a five-second resolvability check per remote host; large clusters or slow DNS/network conditions can make `/info` slower. Environment redaction is pattern-based and may miss secrets that do not match known names, contain `password`, or end in `key`, though it covers core MinIO/KMS variables. Conversely, benign variables ending in `key` are redacted. The function includes environment variable names even when values are redacted, which can still reveal configuration shape.

`PoolNumber` uses `math.MaxInt` for unset/multiple-pool cases, so callers must use `PoolNumbers` for accurate multi-pool reporting. The address choice differs between standalone and distributed erasure modes, and `r` can be nil for internal health generation.

## Test Signals
`TestAdminServerInfo` in `admin-handlers_test.go` indirectly covers this function by calling `/info` through the router and verifying the response region in a single-node erasure setup. The test does not assert redaction, runtime stats, network classification, pool-number behavior, or offline object-layer behavior.
