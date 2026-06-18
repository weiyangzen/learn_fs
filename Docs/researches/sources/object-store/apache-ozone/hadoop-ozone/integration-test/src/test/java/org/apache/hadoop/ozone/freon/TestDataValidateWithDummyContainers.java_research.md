# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/freon/TestDataValidateWithDummyContainers.java

Purpose: Concrete `TestDataValidate` variant for non-persistent dummy containers, where write validation is intentionally unsupported.

Important APIs, types, and functions: Extends `TestDataValidate`. `init` sets `HDDS_CONTAINER_PERSISTDATA=false` and disables unsafe byte operations before starting the inherited cluster. Overrides `validateWriteTest` as a logged no-op. `shutdown` delegates to `shutdownCluster`.

Control flow: Before all tests, it starts a cluster configured to avoid persisting container data. The inherited `ratisTestLargeKey` can still exercise generator behavior, but write-validation test is skipped because non-persistent containers cannot validate writes. After all tests, it shuts down the shared cluster.

State and persistence behavior: Container data persistence is disabled, so data is not durable on disk. This is the core reason validation is not meaningful in this mode.

Dependencies and integration points: Validates Freon behavior under `ChunkManagerDummyImpl`/non-persistent container configuration while sharing the base RandomKeyGenerator cluster harness.

Risks: The no-op override has no assertion, intentionally suppressing the inherited validation contract. If non-persistent behavior changes, this skip may need revisiting.

Test signals: Startup/shutdown and inherited tests are the main signals; overridden validation emits a log message and no assertion.
