# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OmMetadataReader.java

Purpose: `OmMetadataReader` implements `IOmMetadataReader` for live OM and snapshot-backed readers. It centralizes read-side bucket-link resolution, ACL checks, metrics, audit logging, and delegation to key/prefix/volume/bucket managers.

Important APIs and types: public read APIs include `lookupKey`, `getKeyInfo`, `listStatus`, `listStatusLight`, `getFileStatus`, `lookupFile`, `listKeys`, `listKeysLight`, `getAcl`, `getObjectTagging`, and ACL-check helpers. It implements `Auditor` with success/failure audit message builders.

Control flow: each operation resolves bucket links, updates arguments to real volume/bucket names, optionally checks ACLs, increments operation metrics, delegates to the relevant manager, logs audit success/failure, and records performance latency where configured. S3-authenticated requests map access IDs to principals for ACL checks. `getClientAddress()` handles both RPC and gRPC client-address contexts.

State and persistence: this class has no durable state. It reads from managers backed by OM metadata and emits process-local metrics/audit logs.

Dependencies and integration points: depends on `KeyManager`, `PrefixManager`, `VolumeManager`, `BucketManager`, `OzoneManager`, `IAccessAuthorizer`, audit classes, `OmMetadataReaderMetrics`, and `OMPerformanceMetrics`. `OmSnapshot` reuses it with snapshot-aware managers and authorizer.

Risks: ACL checks must use resolved bucket owners and correct resource type, especially for links and S3 contexts. Audit maps must represent original user inputs while operations use resolved names. A metric wiring issue appears in object tagging resolution using lookup resolve latency rather than the object-tagging resolve metric.

Test signals: cover successful and failed audit logging, ACL enabled/disabled behavior, S3 principal resolution, bucket-link resolution, list page-size limiting, object tagging failure metrics, gRPC client address fallback, and `throwIfPermissionDenied` behavior.
