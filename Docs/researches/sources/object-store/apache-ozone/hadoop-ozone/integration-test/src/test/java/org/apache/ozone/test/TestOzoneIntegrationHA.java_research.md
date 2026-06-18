# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/ozone/test/TestOzoneIntegrationHA.java

Purpose: This concrete class instantiates the `HATests` harness as a runnable HA integration suite.

Important APIs and types: It extends `HATests` and returns `MiniOzoneHAClusterImpl` from `createCluster`.

Control flow: `createCluster` simply calls `newClusterBuilder().build()`. The HA builder is configured by the parent with random OM/SCM service IDs and three OMs/SCMs.

State and persistence behavior: Persistent and runtime state comes from the shared HA cluster and nested suites inherited from `HATests`. This class does not add state of its own.

Dependencies and integration points: It is the executable bridge between the abstract HA grouping harness and the JUnit runner.

Risks: All risks are inherited from `HATests`: shared HA state, leadership changes, metrics state, and cleanup interactions among nested tests.

Test signals: Signals are inherited nested HA suite outcomes after the cluster builds and reaches readiness.
