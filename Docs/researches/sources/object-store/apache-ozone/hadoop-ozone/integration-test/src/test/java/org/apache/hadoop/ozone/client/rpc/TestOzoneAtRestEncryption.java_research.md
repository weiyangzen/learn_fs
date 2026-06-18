<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestOzoneAtRestEncryption.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestOzoneAtRestEncryption.java

Purpose: This integration test validates transparent data encryption at rest for normal keys, stream keys, OFS filesystem writes, link buckets, GDPR metadata deletion, encrypted multipart uploads, and key-provider cache lifecycle.

Important APIs/types/functions: Setup starts `MiniKMS`, enables secure OM/block tokens with `CertificateClientTestImpl` and `SecretKeyTestClient`, creates a KMS key through `KeyProvider`, starts the OM secret manager, and configures block/chunk sizes. Main APIs include `BucketArgs.setBucketEncryptionKey`, `OzoneBucket.createKey`, `createStreamKey`, `readKey`, `FileSystem` OFS writes, `OzoneKeyDetails.getFileEncryptionInfo`, `ClusterContainersUtil.verifyOnDiskData`, `bucket.initiateMultipartUpload`, `createMultipartKey`, `createMultipartStreamKey`, `completeMultipartUpload`, `MultipartInputStream`, OM deleted table scanning, and `RpcClient.getKeyProviderCache`.

Control flow: The setup installs a KMS provider URI, starts a 10-datanode cluster, sets a 256 KiB minimum MPU part size, creates `TEST_KEY`, and configures OFS as default FS. Tests warm up OM EDEK cache after OM restart, create encrypted buckets for every `BucketLayout`, verify direct/stream/OFS writes, verify link buckets inherit encryption, and ensure overwrites get distinct encryption info. GDPR tests delete encrypted keys and assert deleted-table metadata no longer retains GDPR secret fields or file encryption info. MPU tests upload one to three encrypted parts through byte-array and stream paths, complete uploads, read through `MultipartInputStream`, and exercise seeks/reads around crypto buffer, chunk, and block boundaries. `testGetKeyProvider` checks cached key providers are reused and closed on client close.

State and persistence behavior: The tests verify OM key metadata includes `FileEncryptionInfo` while live, deleted table entries are scrubbed, KMS EDEK queues are populated, on-disk container data differs from plaintext, multipart part ETags are committed, and final multipart keys are readable at arbitrary offsets.

Dependencies and integration points: Integrates KMS, Hadoop crypto buffer sizing, secure OM flags, block tokens, SCM/container storage, OFS filesystem adapter, Object Store and FSO bucket layouts, OM metadata tables, deleted-table cleanup, and multipart read composition.

Risks: The test is expensive and timing-sensitive around KMS cache warmup and OM restart. Encryption assertions depend on local container disk inspection. MPU stream cases are marked flaky, likely due to stream finalization or multipart read timing.

Test signals: Passing proves encrypted buckets decrypt through client APIs, persist ciphertext on disk, avoid leaking sensitive deleted metadata, support encrypted multipart uploads, and manage key-provider cache resources.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestOzoneAtRestEncryption.java -->
