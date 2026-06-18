# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/upgrade/FinalizationManagerTestImpl.java

Purpose: This test helper subclasses `FinalizationManagerImpl` so tests can inject a custom `FinalizationStateManager`. It exists to make SCM upgrade-finalization tests deterministic without using the production builder's normal state-manager construction path.

Important APIs and types: The class extends `FinalizationManagerImpl` and implements `FinalizationManager`. Its nested `Builder` extends `FinalizationManagerImpl.Builder`, adds `setFinalizationStateManager(FinalizationStateManager)`, and overrides `build` to create `FinalizationManagerTestImpl`.

Control flow: Tests configure the inherited builder fields, call `setFinalizationStateManager`, and then `build`. The constructor delegates to the parent constructor overload with both the builder and injected state manager.

State and persistence behavior: This class persists no data itself. It influences persistence indirectly by allowing tests to use mocked finalization tables, transaction buffers, Ratis server stubs, and version managers inside the production finalization manager flow.

Dependencies and integration points: It is tightly coupled to `FinalizationManagerImpl.Builder` and the protected or package-visible constructor signature that accepts an explicit state manager. `TestScmFinalization` uses it to drive resume and checkpoint behavior.

Risks: The helper bypasses some production construction logic; if the production builder adds mandatory validation or side effects, tests using this helper may miss them. It also relies on superclass builder field compatibility.

Test signals: The helper is validated indirectly when `TestScmFinalization` can inject mocked state and verify finalization ordering, persisted marks, and status messages.
