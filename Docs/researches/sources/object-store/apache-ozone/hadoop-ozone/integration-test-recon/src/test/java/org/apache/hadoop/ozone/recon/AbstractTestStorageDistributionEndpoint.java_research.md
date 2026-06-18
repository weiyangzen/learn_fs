<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/AbstractTestStorageDistributionEndpoint.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/AbstractTestStorageDistributionEndpoint.java

Purpose: abstract integration-test fixture for Recon storage distribution and pending-deletion endpoints. It centralizes MiniOzoneCluster setup, object creation helpers, OM sync, REST polling assertions, and cleanup.

Important APIs: static `initializeCluster(numDatanodes)` configures aggressive OM/SCM/DN intervals, starts `MiniOzoneCluster` with `ReconService`, waits for readiness, and creates OM/SCM/client handles. `createVolumeAndBucket` creates an FSO bucket with a supplied default replication config. `createOpenKeysAndMultipartKeys` writes open key and multipart state through OM/client APIs. Verification methods poll Recon REST endpoints for `/api/v1/storageDistribution` and `/api/v1/pendingDeletion?component=om|scm|dn`, parse JSON into Recon API types, and assert totals. `syncDataFromOM` directly invokes `OzoneManagerServiceProviderImpl.syncDataFromOM`. `closeAllContainers` fires SCM close events. `cleanup` deletes all filesystem root entries after each test and closes FS; `tear` shuts down the cluster.

Control flow and integration: tests call subclass-specific cluster initialization, create keys/deletions, sync Recon from OM, then retry endpoint assertions until asynchronous Recon/SCM/DN metrics converge. The fixture compares Recon storage totals with SCM datanode usage protos and validates pending deletion at OM metadata, SCM block deletion, and datanode metric layers.

State and persistence: static cluster, conf, OM, SCM, client, and Recon service are shared per subclass. Recon DBs are configured by `ReconService` under the cluster metadata dir. Test FS state is cleaned between methods.

Risks and tests: static shared state requires careful subclass lifecycle. Assertions are wrapped in boolean retry helpers that log debug details, so failures may surface only after wait loops in subclasses. Hardcoded expected byte totals assume specific key counts and replication behavior. Timing-sensitive endpoints need adequate polling. This fixture is itself not tested except through concrete subclasses.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/AbstractTestStorageDistributionEndpoint.java -->
