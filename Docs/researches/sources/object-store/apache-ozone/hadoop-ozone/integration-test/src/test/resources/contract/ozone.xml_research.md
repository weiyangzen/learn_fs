# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/resources/contract/ozone.xml

Purpose: This Hadoop filesystem contract file declares Ozone/OFS object-store semantics for contract tests.

Important APIs and types: It is an XML `<configuration>` resource consumed by Hadoop contract tests. Keys include `fs.contract.test.root-tests-enabled`, random seek count, blobstore classification, delayed create visibility, case sensitivity, rename behavior, append/concat/block-locality support, getFileStatus/seek/unbuffer support, strict exceptions, permissions support, hsync, and hflush.

Control flow: There is no code flow. Test harnesses load the XML as configuration and use the properties to enable, skip, or adjust contract tests.

State and persistence behavior: The file is static test configuration. It does not persist runtime state.

Dependencies and integration points: It integrates Ozone with Hadoop FS contract suites and tells tests which filesystem features should or should not be expected from an object store. It directly affects assertions in contract tests such as seek, rename, append, delete, and sync tests.

Risks: Incorrect flags can either hide real regressions by skipping/weakening tests or cause false failures by claiming unsupported semantics. Rename and create-visibility flags are especially important for object-store behavior.

Test signals: Contract tests use these properties as expected behavior signals: Ozone is a blobstore, case-sensitive, create visibility may be delayed, append/atomic directory delete/atomic rename/block locality/concat/Unix permissions are unsupported, while getFileStatus, seek, seek-on-closed, strict exceptions, unbuffer, hsync, and hflush are supported.
