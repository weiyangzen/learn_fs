# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/upgrade/TestNSSummaryAggregatedTotalsUpgrade.java

Purpose: Tests `NSSummaryAggregatedTotalsUpgrade`, an upgrade action that triggers an NSSummary rebuild through the globally available Recon task controller.

Important APIs and control flow: Each test statically mocks `ReconGuiceServletContextListener.getGlobalInjector`, resolves `ReconTaskController`, and stubs `queueReInitializationEvent(MANUAL_TRIGGER)`. It verifies execute behavior for `SUCCESS`, `RETRY_LATER`, and `MAX_RETRIES_EXCEEDED`, plus failure when the injector is null and propagation when injector lookup throws.

State and persistence behavior: The upgrade itself does not directly mutate SQL in these tests; it triggers asynchronous rebuild scheduling. Static global injector state is mocked and scoped with try-with-resources.

Dependencies and integration points: Integrates upgrade execution, Guice global injector access, and `ReconTaskController` reinitialization API. It ties schema/layout upgrade flow to namespace-summary aggregate recomputation.

Risks and test signals: Good signal that upgrade dispatches a rebuild and handles missing injector. It does not verify eventual rebuild completion or durable NSSummary/global-stat changes, only queueing behavior.
