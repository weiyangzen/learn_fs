# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/ozone/test/TestOzoneIntegrationNonHA.java

Purpose: This concrete class instantiates the broad `NonHATests` harness as a runnable non-HA integration suite.

Important APIs and types: It extends `NonHATests`, returns `MiniOzoneCluster`, and uses JUnit `@TestInstance(PER_CLASS)`.

Control flow: `createCluster` calls the inherited `newClusterBuilder().build()`, using the common base configuration and default five-datanode non-HA cluster unless parent hooks change it.

State and persistence behavior: Runtime and persistent state are created by the nested non-HA suites inherited from `NonHATests`. This class has no additional state.

Dependencies and integration points: It is the runnable entry point for the aggregated non-HA integration suite.

Risks: The class inherits the large shared-cluster contamination surface of `NonHATests`. There are no local assertions to narrow failures.

Test signals: Signals are successful execution of all nested non-HA suites on the built mini cluster.
