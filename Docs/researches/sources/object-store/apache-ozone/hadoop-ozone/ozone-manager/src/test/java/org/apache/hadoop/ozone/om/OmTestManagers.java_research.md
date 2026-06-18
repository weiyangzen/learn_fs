<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/OmTestManagers.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/OmTestManagers.java

Purpose: Test utility that creates a lightweight local OM, exposes its managers, and supplies an RPC write client for unit/integration-style OM tests.

Important APIs/types/functions: Constructors accept `OzoneConfiguration` and optional SCM block/container clients. Getters expose `OzoneManagerProtocol`, `OzoneManager`, `KeyManager`, `OMMetadataManager`, `VolumeManager`, `BucketManager`, `PrefixManager`, SCM block client, and `OzoneClient`. `kmsProviderInit` injects a mock KMS provider. `stop` closes the RPC client and stops OM.

Control flow: The constructor sets SCM client address, mini-cluster metrics mode, initializes `OMStorage`, enables test secure OM flag, creates OM, extracts internal managers with whitebox utilities, replaces SCM clients and block token secret manager, starts OM, waits for Ratis leader-ready status, creates an RPC client, and captures manager references.

State and persistence behavior: Initializes an OM metadata directory from the supplied config and mutates OM internals for tests. It does not clean the metadata directory itself beyond caller temp-dir lifecycle. It owns resources that must be stopped.

Dependencies and integration points: Used by bucket-manager tests and other OM tests needing a real OM without a full cluster. Depends on `ScmBlockLocationTestingClient`, mocked `StorageContainerLocationProtocol`, whitebox state mutation, Ratis readiness, and `OzoneClientFactory`.

Risks: Whitebox field names make the utility brittle to OM internals. It sets global/static test flags and metrics mini-cluster mode. `cleanup` in some tests stops OM directly rather than calling `stop`, which can leak RPC client resources. Waiting only 10 seconds for leader readiness can be timing-sensitive.

Test signals: Tests using this helper verify real OM manager behavior through RPC while keeping SCM fake. Failures often indicate OM startup, Ratis readiness, manager injection, or cleanup issues rather than the target test alone.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/OmTestManagers.java -->
