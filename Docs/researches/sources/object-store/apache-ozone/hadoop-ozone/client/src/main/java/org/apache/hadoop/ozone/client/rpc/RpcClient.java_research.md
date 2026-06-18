# sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/rpc/RpcClient.java

## Purpose
`RpcClient` is the RPC-backed implementation of `ClientProtocol` for the Ozone Java client. It is the main client-side bridge from public `OzoneClient`, `ObjectStore`, `OzoneVolume`, and `OzoneBucket` operations to OM RPCs and datanode container IO. It owns the OM protocol proxy, xceiver client factory, client metrics handle, byte-buffer pool, KMS provider cache, stream builders, and OM-version feature gates used by keys, files, multipart uploads, S3 paths, tenants, snapshots, ACLs, object tagging, and lease recovery.

## Important APIs, Types, And Functions
The constructor wires `ConfigurationSource`, current `UserGroupInformation`, `ReplicationConfigValidator`, `OzoneClientConfig`, OM transport/proxy, `XceiverClientFactory`, `BoundedElasticByteBufferPool`, `BlockInputStreamFactory`, `ContainerClientMetrics`, memoized EC reconstruction and write executors, and server-default/KMS cache settings. `createOmTransport` and `createXceiverClientFactory` are `@VisibleForTesting` hooks heavily used by tests in this subset to inject `MockOmTransport` and `MockXceiverClientFactory`.

Volume and bucket APIs include `createVolume`, `setVolumeOwner`, `setVolumeQuota`, `getVolumeDetails`, `listVolumes`, `createBucket`, bucket property setters, `deleteBucket`, `getBucketDetails`, and `listBuckets`. These validate names and quotas, translate public argument objects into OM helper objects such as `OmVolumeArgs`, `OmBucketInfo`, and `OmBucketArgs`, and delegate persistence to `ozoneManagerClient`.

Key/file APIs include `createKey`, `rewriteKey`, `createKeyIfNotExists`, `rewriteKeyIfMatch`, stream variants, `getKey`, `getKeysEveryReplicas`, `deleteKey(s)`, `renameKey(s)`, `listKeys`, `getKeyDetails`, `headObject`, `createFile`, `createStreamFile`, `readFile`, and status listings. They build `OmKeyArgs`, call OM open/get/lookup APIs, and create `OzoneOutputStream`, `OzoneDataStreamOutput`, or `OzoneInputStream` instances around `KeyOutputStream`, `ECKeyOutputStream`, `KeyDataStreamOutput`, `KeyInputStream`, `ECBlockInputStream`, and crypto wrappers.

Multipart APIs cover initiation, part stream creation, completion with optional generation/ETag constraints, abort, part listing, and upload listing. Security/admin APIs cover delegation tokens, S3 secrets, tenant creation/deletion/user/admin operations, S3 context lookup, S3 auth thread locals, ACL operations, snapshots and snapshot diff jobs, bucket owner updates, timestamps, lease recovery, and object tagging.

## Control Flow
Construction first builds the OM transport and translator, retrieves service info, computes the minimum OM version visible in the service list, checks S3-auth version requirements when security is enabled, then creates the xceiver client manager and stream support objects. Most public mutating methods follow a pattern: validate public names/arguments, check `omVersion` for feature availability, build an OM helper/protobuf-friendly argument object, and call the OM protocol.

Write control flow goes through `createWriteKeyArgsBuilder` or `createStreamKeyArgsBuilder`, then `ozoneManagerClient.openKey` or `createFile`, then stream creation. `createKeyOutputStream` selects `ECKeyOutputStream.Builder` for EC replication and regular `KeyOutputStream.Builder` otherwise; both receive xceiver manager, OM client, unsafe byte-buffer setting, client config, metrics, write executor supplier, stream buffer args, and OM version. Data stream output uses `KeyDataStreamOutput` only for RATIS; non-RATIS falls back to normal output streams.

Read control flow resolves `OmKeyInfo` via optimized `getKeyInfo` when supported or legacy `lookupKey` otherwise. `getInputStreamWithRetryFunction` passes a retry callback that refreshes key location info from OM with container-cache refresh enabled. `createInputStream` then selects plain `KeyInputStream`, GDPR cipher wrapper, KMS crypto stream, or multipart crypto stream depending on file encryption info and metadata.

## State And Persistence Behavior
`RpcClient` itself does not persist Ozone metadata. Persistent state lives in OM and datanodes; this class constructs and submits requests that change volumes, buckets, keys, multipart uploads, tenants, ACLs, snapshots, tags, and lease state. Local state includes cached `KeyProvider`s keyed by URI, memoized executors, `serverDefaults` and update timestamp, byte-buffer pool capacity, metrics handle, delegation-token service text, `s3gUgi`, and thread-local S3 auth delegated through the OM client.

The key-provider cache closes providers through a removal listener. `close()` shuts down initialized executors, closes OM and xceiver clients, invalidates/cleans the key-provider cache, and releases metrics. Server defaults are refreshed lazily after `serverDefaultsValidityPeriod`.

## Dependencies And Integration Points
This file integrates with OM via `OzoneManagerClientProtocol` and `OzoneManagerProtocolClientSideTranslatorPB`, with SCM/datanodes via `XceiverClientFactory`, `KeyOutputStream`, and input stream factories, with KMS via `OzoneKMSUtil` and Hadoop `KeyProvider`, with security via `UserGroupInformation`, delegation tokens, S3 auth, and TLS trust manager setup, and with versioned OM behavior through `OzoneManagerVersion`.

Important feature gates include EC storage, optimized get-key-info, lightweight key/status listings, atomic rewrite/create, object tags, S3 part-aware get, S3 object tagging APIs, multipart pagination, and HBase lease recovery. Tests in this subset override `createOmTransport` and `createXceiverClientFactory` to make this production class run against in-memory OM and datanode mocks.

## Risks And Edge Cases
Many methods depend on OM-version comparisons; missing or stale service info can accidentally use a fallback path or reject a newer feature. Quota validation throws `IllegalArgumentException` despite declaring `OMException`, so callers must tolerate unchecked validation failures. `getKeysEveryReplicas` mutates the `keyInfo` location versions while iterating replicas, which is convenient for stream construction but risky if callers reuse that object. `setThreadLocalS3Auth` assumes `getThreadLocalS3Auth()` is non-null after delegation and can throw if passed null. `getKeyProvider()` logs and returns null on provider creation failure, pushing failure later into crypto paths.

The stream construction paths are sensitive to replication config type. EC writes depend on executor, byte-buffer-pool, preallocated block, and S3 credential plumbing. Encryption handling splits between KMS file encryption and metadata-driven GDPR symmetric encryption, and malformed metadata or missing JCE/KMS support will surface as IO failures.

## Test Signals
The files in this work item exercise `RpcClient` through injected mocks rather than external services. `TestOzoneClient` covers volume/bucket/key creation, deletion, RATIS writes, block allocation, and EC key creation. `TestBlockOutputStreamIncrementalPutBlock` covers hsync with incremental and full chunk lists. `TestOzoneECClient` stresses EC output-stream behavior, retries, partial stripes, block metadata, and reads. `TestFileChecksumHelper` and `TestReplicatedBlockChecksumComputer` cover checksum integration with mocked OM/xceiver clients. Snapshot, replication-config utility, and package tests cover adjacent client-facing behavior.
