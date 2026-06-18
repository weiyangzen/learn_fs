# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/freon/TestDataValidateWithUnsafeByteOperations.java

Purpose: Concrete `TestDataValidate` variant that runs Freon write-validation tests with unsafe byte operations enabled.

Important APIs, types, and functions: Extends `TestDataValidate`. `init` sets `OZONE_UNSAFEBYTEOPERATIONS_ENABLED=true` and starts the inherited cluster. `shutdown` calls `shutdownCluster`.

Control flow: Starts a five-datanode Ratis cluster configured for unsafe byte operations, then inherits large-key and multi-key RandomKeyGenerator validation tests. Shuts down after all tests.

State and persistence behavior: Uses persistent replicated key data, but byte-buffer handling follows the unsafe optimized path. Counters and validation data are maintained by `RandomKeyGenerator`.

Dependencies and integration points: Verifies Freon validation and Ozone write/read data handling work with the unsafe byte operation optimization enabled.

Risks: Thin wrapper; failures indicate either base Freon validation issues or unsafe byte path regressions. Does not add mode-specific assertions beyond inherited validation success.

Test signals: Inherited tests must produce expected object counts, positive validation counts, and zero failed validations.
