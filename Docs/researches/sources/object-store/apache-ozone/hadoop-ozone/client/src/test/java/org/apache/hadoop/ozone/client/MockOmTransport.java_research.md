# sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/MockOmTransport.java

## Purpose
`MockOmTransport` implements `OmTransport` with in-memory OM state so Ozone client unit tests can run without an OM service. It handles a deliberately small set of OM commands needed by client write/read tests.

## Important APIs, Types, And Functions
The constructor accepts a `MockBlockAllocator`, defaulting to `SinglePipelineBlockAllocator`. `submitRequest` switches on OM command type and supports volume create/info/delete, bucket create/info, key create/commit/lookup/get-info, service list, open-file list, and allocate-block. `createKey` allocates initial locations and resolves replication from key args, bucket default replication, or RATIS THREE fallback. `commitKey` moves an open key to committed keys unless the request is hsync, preserving replication details and committing locations from `KeyArgs`. `getKeys` exposes committed key state for assertions.

## Control Flow
Requests enter `submitRequest`, dispatch to command-specific helpers, and are wrapped by `response`, which converts `MockOmException` into unsuccessful `OMResponse` statuses. `createVolume` initializes nested bucket/open-key/key maps. `createBucket` stores bucket info and initializes per-bucket key maps. `createKey` creates an open `KeyInfo` with allocated locations. `commitKey` reads the open key, optionally removes it, builds committed key info from request key locations and sizes, and stores it in `keys`.

## State And Persistence Behavior
State is all in-memory: `volumes`, `buckets`, `openKeys`, and `keys`. It models OM metadata persistence for a single test process. Hsync commits keep the open key present while writing committed key state, which is important for incremental hsync tests. No concurrency control, deletion cleanup beyond volume map removal, or full OM validation is provided.

## Dependencies And Integration Points
It integrates with `RpcClient` via the `createOmTransport` test override and with stream code through protobuf OM responses. It depends on `MockBlockAllocator` for pipeline and block allocation, `DefaultReplicationConfig`/`ReplicationConfig` for bucket defaults, and OM protobuf request/response classes.

## Risks And Edge Cases
Unsupported OM calls throw `IllegalArgumentException`, so tests must stay inside the modeled surface. Many nested map lookups assume volumes/buckets/keys exist. `deleteVolume` removes only `volumes`, leaving other maps behind. `serviceList` returns an empty response, so production code paths requiring rich service metadata may not be accurately modeled. Replication defaulting is simplified.

## Test Signals
Used by `TestOzoneClient`, `TestBlockOutputStreamIncrementalPutBlock`, `TestOzoneECClient`, and `TestFileChecksumHelper`. These tests validate volume/bucket creation, key open/commit/read, EC block allocation, default replication propagation, hsync behavior, and committed-key metadata.
