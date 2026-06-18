# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/upgrade/FinalizationStateManagerTestImpl.java

Purpose: This compact helper exposes a `FinalizationStateManagerImpl` variant that can be built directly for tests without the production invocation-handler wiring. It simplifies mocked SCM finalization-state tests.

Important APIs and types: The class extends `FinalizationStateManagerImpl` and implements the `FinalizationStateManager` contract through inheritance. Its nested `Builder` extends `FinalizationStateManagerImpl.Builder` and overrides `build` to return the test implementation.

Control flow: Test code configures the inherited builder with a finalization store table, Ratis server, transaction buffer, and upgrade finalizer, then calls `build`. The constructor simply delegates to `super(builder)`.

State and persistence behavior: The helper owns no additional state beyond what the superclass builder initializes. Its value is enabling tests to control where the finalizing marker, layout-version key, and in-memory checkpoint state are read and written.

Dependencies and integration points: It is used by `TestScmFinalization` with mocked `Table<String, String>`, `SCMRatisServer`, `DBTransactionBuffer`, and `SCMUpgradeFinalizer` instances.

Risks: Like most test-only subclasses, it can hide production construction behavior if the production manager gains required invocation-handler semantics. It also depends on the parent builder remaining extensible.

Test signals: Indirect signals are successful checkpoint mapping, `crossedCheckpoint` behavior, and resume-finalization assertions in the finalization test suite.
