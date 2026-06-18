# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/upgrade/TestReplicatedSizeOfFilesUpgradeAction.java

Purpose: Tests `ReplicatedSizeOfFilesUpgradeAction`, which triggers an NSSummary rebuild so replicated-size fields can be recomputed during upgrade.

Important APIs and control flow: Static mocks provide the global Guice injector, which returns a mocked `ReconTaskController`. The success test verifies `queueReInitializationEvent` is called once. The failure test makes the controller throw and asserts the upgrade wraps it in a `RuntimeException` with message `Failed to rebuild NSSummary during upgrade`.

State and persistence behavior: No direct SQL mutation is verified. The upgrade action delegates state recomputation to Recon task reinitialization.

Dependencies and integration points: Uses `ReconGuiceServletContextListener`, Guice `Injector`, `ReconTaskController`, and `ReconTaskReInitializationEvent.ReInitializationReason`. It is part of Recon layout/schema upgrade flow.

Risks and test signals: Moderate signal for dispatch and exception wrapping. It does not verify handling of non-success enum results or actual rebuilt replicated sizes.
