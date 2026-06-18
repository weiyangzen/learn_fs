# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/freon/TestDataValidateWithSafeByteOperations.java

Purpose: Concrete `TestDataValidate` variant that runs Freon write-validation tests with unsafe byte operations disabled.

Important APIs, types, and functions: Extends `TestDataValidate`. `init` creates `OzoneConfiguration`, sets `OZONE_UNSAFEBYTEOPERATIONS_ENABLED=false`, and calls `startCluster`. `shutdown` calls `shutdownCluster`.

Control flow: Before all tests, starts the inherited five-datanode Ratis cluster in safe byte-operation mode. It inherits `ratisTestLargeKey` and `validateWriteTest`, which run `RandomKeyGenerator` with write validation. After all tests, it shuts down the cluster.

State and persistence behavior: Uses normal persistent containers and safe byte handling for generated key data. State and validation counters are inherited from the base test.

Dependencies and integration points: Verifies Freon validation works when Ozone avoids unsafe byte operations, covering the safer data path.

Risks: Thin wrapper, so most behavioral risk is in base class. It only toggles one config key and assumes inherited tests fully cover the mode.

Test signals: Inherited creation-count and validation-count assertions must pass under safe byte operations.
