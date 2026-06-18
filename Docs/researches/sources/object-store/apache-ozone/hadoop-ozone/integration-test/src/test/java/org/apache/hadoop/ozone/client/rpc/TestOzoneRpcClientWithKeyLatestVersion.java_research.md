<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestOzoneRpcClientWithKeyLatestVersion.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestOzoneRpcClientWithKeyLatestVersion.java

Purpose: This abstract non-HA test verifies that the client option `OZONE_CLIENT_KEY_LATEST_VERSION_LOCATION` controls whether key location versions returned by listing include only the latest version or all versions when bucket versioning is enabled.

Important APIs/types/functions: It uses `NonHATests.TestCase.cluster`, `OzoneClientFactory.getRpcClient`, `ObjectStore`, `OzoneVolume`, `OzoneBucket`, `BucketArgs.setVersioning`, `TestDataUtil.createKey`, `assertKeyContent`, `bucket.listStatus`, and `bucket.listStatusLight`.

Control flow: The parameterized test runs with `getLatestVersionOnly` true and false. For each mode it creates a client using the cluster config plus the option override, creates a volume, then creates two buckets: one with versioning disabled and one enabled. It writes the same key multiple times, ending with known content, verifies read content, and asserts the number of `KeyLocationVersions` returned by `listStatus`: all versions only when bucket versioning is enabled and the client option asks not to limit to latest; otherwise one version. The light-listing API is checked for a single returned status entry.

State and persistence behavior: The test creates actual key versions in OM. It validates client-side projection of those persisted versions rather than physical block contents.

Dependencies and integration points: Integrates OM versioned-key metadata, client configuration propagation, listing APIs, and read-after-overwrite semantics.

Risks: Expected version count depends on overwrite preserving previous versions only for versioned buckets. Changes to `listStatusLight` version exposure are not deeply asserted here.

Test signals: Passing confirms latest-version filtering is honored without breaking key reads or list status shape.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestOzoneRpcClientWithKeyLatestVersion.java -->
