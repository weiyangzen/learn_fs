<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestSecureOzoneRpcClient.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestSecureOzoneRpcClient.java

Purpose: This secure subclass of `OzoneRpcClientTests` validates RPC client behavior with block tokens, native ACL authorization, S3 authentication, secure server defaults, and FSO lease recovery.

Important APIs/types/functions: Setup enables secure OM test mode, block tokens, ACLs, native authorizer, HBase enhancements, hsync, test authorization, certificate and secret-key test clients, KMS provider URI, and inherited cluster startup. The class uses `OzoneOutputStream.hsync`, `RootedOzoneFileSystem.recoverLease`, `OMMetrics`, OM metadata/deleted tables, `S3SecretManager`, signed `OMRequest` messages, `UserGroupInformation` proxy users, and inherited `verifyReplication`.

Control flow: `testPutKeySuccessWithBlockToken` writes and reads multiple keys in object-store and FSO buckets, verifies committed-byte metrics, and asserts block tokens are not persisted in OM key location metadata or cache. `testFileRecovery` writes and hsyncs an FSO key, optionally forces lease recovery through a system property, and expects close failure only after forced recovery has committed the key. `testPreallocateFileRecovery` creates a preallocated key, writes less than reserved size, recovers the lease, then checks file length, committed bytes, quota, and deleted-table entries for unused preallocated blocks. `testS3Auth` stores an S3 secret, submits signed create/read volume OM requests, verifies OK responses, then changes the secret and expects invalid-token responses. `testRemoteException` checks unauthorized proxy-user volume listing raises `AccessControlException`. It overrides an unhealthy-container read test because DN restart is incompatible with security enabled and verifies server defaults expose the KMS URI.

State and persistence behavior: State assertions include OM metrics, key tables/cache entries without tokens, FSO committed file metadata, bucket namespace/byte quota, deleted-table reclaimed block records, S3 secret table authentication behavior, and server defaults.

Dependencies and integration points: Integrates block-token security, OM native ACL authorizer, secure datanode/container access, OFS filesystem lease recovery, KMS server-default propagation, S3 auth validation, and inherited broad RPC client tests.

Risks: Security setup is configuration-heavy. System property `FORCE_LEASE_RECOVERY_ENV` and FS cache disabling can leak if not isolated. Preallocation recovery uses large data sizes and asynchronous quota/deleted-table updates.

Test signals: Passing confirms secure client writes/readbacks work, tokens are not persisted in metadata, recovery commits correct sizes and reclaims unused blocks, S3 signatures are enforced, and secure server defaults are exposed.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestSecureOzoneRpcClient.java -->
