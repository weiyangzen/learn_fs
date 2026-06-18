## sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/ObjectStore.java

### Purpose
`ObjectStore` is the top-level object-store facade exposed from `OzoneClient`. It owns a `ClientProtocol` proxy and offers volume, S3 bucket, tenant, ACL, delegation-token, snapshot, compaction DAG, and snapshot-diff operations. The class is deliberately thin: it converts client-facing operations into `ClientProtocol` calls, adds paged iterators for list APIs, and handles a few compatibility or error-mapping cases.

### Important APIs and Types
- Construction captures `ClientProtocol`, list cache size from `HddsClientUtils`, and S3 default bucket layout from `OzoneConfigKeys.OZONE_S3G_DEFAULT_BUCKET_LAYOUT_KEY`.
- Volume APIs: `createVolume`, `getVolume`, `listVolumes`, `listVolumesByUser`, `deleteVolume`.
- S3 APIs: `createS3Bucket`, `getS3Bucket`, `deleteS3Bucket`, S3 secret getters/setters/revoke, and `getS3VolumeContext`.
- Tenant APIs: create/delete tenant, assign/revoke user access IDs, assign/revoke tenant admins, list users, get user info, list tenants.
- ACL APIs delegate `addAcl`, `removeAcl`, `setAcl`, and `getAcl` for generic `OzoneObj`.
- Snapshot APIs cover create/rename/delete/get/list snapshots and sync or async snapshot-diff operations.
- Nested iterators: `VolumeIterator`, `SnapshotIterator`, and `SnapshotDiffJobIterator` implement paged remote listing.

### Control Flow
Most methods are one-hop delegations to `proxy`. `createS3Bucket` first resolves the S3 volume, then creates the bucket with the configured S3 bucket layout; if OM reports `NOT_SUPPORTED_OPERATION_PRIOR_FINALIZATION`, it retries with `BucketLayout.LEGACY` for pre-finalized clusters. `deleteS3Bucket` maps a missing S3 volume to `BUCKET_NOT_FOUND`, matching bucket-level semantics for S3 clients. The list iterators fetch an initial page in the constructor, then call the appropriate proxy list method again when the current page is exhausted and a last value or continuation marker exists.

### State and Persistence Behavior
The only local mutable state is `listCacheSize` and `s3BucketLayout`; durable state is maintained by Ozone Manager through `ClientProtocol`. Iterator state is in-memory and includes the last returned volume, snapshot, or snapshot-diff job marker. Delegation tokens and S3 secrets are returned from server-side security services and are not cached locally here.

### Dependencies and Integration Points
This class integrates with `ClientProtocol`, `OzoneVolume`, `OzoneBucket`, OM helper DTOs, Hadoop security token classes, `UserGroupInformation`, `OzoneAcl`, snapshot response types, and S3/tenant helper types. It is the primary bridge from external client code into OM RPC behavior. The default S3 bucket layout is validated through `OmUtils.validateBucketLayout`.

### Risks and Edge Cases
Iterator `hasNext()` wraps `IOException` in `RuntimeException` for volumes but logs and suppresses next-page errors for snapshots and snapshot diff jobs, which can hide remote failures behind short iteration. `createS3Bucket` has intentionally broad compatibility behavior but only handles the specific pre-finalization result code. `listVolumesByUser` resolves an empty user to the current short user name, so tests need a controlled UGI context.

### Test Signals
Useful tests cover paged list iteration across cache boundaries, S3 bucket layout fallback, S3 volume-not-found mapping, tenant delegation paths, snapshot list pagination, snapshot-diff job pagination, and delegation-token proxy forwarding. Mock `ClientProtocol` tests are sufficient for most behavior because the class has limited local logic.
