# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/OMClientRequest.java

## Purpose
`OMClientRequest` is the abstract base for write-side OM request handlers. It defines pre-execution request augmentation, deterministic cache update contract, ACL helpers, user/remote-address extraction, audit helpers, key path normalization, error response creation, and lock detail aggregation.

## Important APIs and Types
- Constructor stores a non-null `OMRequest` and clears `OMLockDetails`.
- `preExecute(OzoneManager)` sets `UserInfo` and metadata layout version before a request is serialized to Ratis.
- Abstract `validateAndUpdateCache(OzoneManager, ExecutionContext)` is implemented by concrete write requests.
- ACL helpers include overloads of `checkAcls` and FSO-specific `checkACLsWithFSO`.
- Authentication helpers include `getUserInfo`, `getUserIfNotExists`, `createUGI`, `createUGIForApi`, `getRemoteAddress`, and `getHostName`.
- Response/audit helpers include `createErrorOMResponse`, `markForAudit`, `buildAuditMessage`, and `buildVolumeAuditMap`.
- Static key helpers normalize and validate key paths based on filesystem paths and `BucketLayout`.

## Control Flow
RPC-side pre-execution calls `preExecute`, which builds a layout-version protobuf from the OM version manager and fills user info if absent. `getUserInfo` prefers S3 authentication access id mapped to user principal, then Hadoop RPC remote user, then existing gRPC user info. Remote address/host are pulled from Hadoop RPC context or gRPC context keys. `getUserIfNotExists` falls back to the current OM process user and OM RPC server address for internal calls.

`validateAndUpdateCache` is the deterministic state-machine phase: subclasses validate, authorize as needed before entering this method, and update metadata caches without direct RocksDB persistence. The class warns not to bring external dependencies such as Ranger checks into this method because all OM replicas must apply the same deterministic updates.

ACL helpers build `OzoneObj` and `RequestContext`, resolve volume/bucket owners, create UGI from request user info, and delegate to `OzoneManager.checkAcls`, `OzoneAclUtils.checkAllAcls`, or `OmMetadataReader.checkAcls`. FSO ACL checks create an `OzonePrefixPathImpl` to support recursive path checks. Error response helpers map exceptions via `OzoneManagerRatisUtils.exceptionToResponseStatus`, using full stack text for non-OM/non-path exceptions.

## State and Persistence Behavior
`OMClientRequest` does not persist directly. It manages request metadata that will be logged through Ratis and establishes the cache-update contract that produces `OMClientResponse` objects. Persistence occurs later in `OzoneManagerDoubleBuffer` when responses write to RocksDB batches. Per-request state includes the protobuf request, cached UGI, cached remote address, audit builder, and accumulated lock details.

## Dependencies and Integration Points
It integrates with `OzoneManager`, `ExecutionContext`, `OMClientResponse`, `OMLockDetails`, `OzoneManagerRatisUtils`, Hadoop RPC/gRPC context, OM metadata readers, ACL utilities, audit logging, `BucketLayout`, and filesystem path validation utilities. Every concrete write request in OM extends this class.

## Risks and Edge Cases
Calling ACL checks inside `validateAndUpdateCache` can cause HA divergence if external authorizers return different results across replicas. `getRemoteAddress` calls `InetAddress.getByName` on request user info and can throw if malformed. User info fallback for internal calls depends on OM RPC server address being available. Key normalization rejects trailing slashes for layouts that normalize paths; callers must choose `normalizeKeyPath` versus `validateAndNormalizeKey` correctly for existing versus new keys. `buildAuditMessage` writes into a reusable builder, so request objects should not be reused across independent operations.

## Test Signals
Tests should cover preExecute user/layout population, S3 access-id user mapping, gRPC and RPC address extraction, internal-call fallback, ACL helper delegation and owner choice, UGI failure mapping to `UNAUTHORIZED`, exception-to-error-response mapping, audit message contents, key path normalization by bucket layout, trailing slash rejection, and lock detail merging.
