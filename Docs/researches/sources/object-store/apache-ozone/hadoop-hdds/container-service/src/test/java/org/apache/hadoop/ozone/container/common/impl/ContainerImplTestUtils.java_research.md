# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/impl/ContainerImplTestUtils.java

Purpose: This is a small test utility class for constructing `ContainerSet` instances backed by mocked `WitnessedContainerMetadataStore` objects. It is not itself a JUnit test but is used throughout this subset to avoid setting up a full metadata store.

Important APIs and types: It exposes `newContainerSet()`, `newContainerSet(long recoveringTimeout)`, `newContainerSet(long recoveringTimeout, WitnessedContainerMetadataStore)`, and `newContainerSet(long recoveringTimeout, Clock)`. It uses Mockito, `InMemoryTestTable`, `WitnessedContainerMetadataStore`, and `ContainerSet`.

Control flow: Default overloads create a mock metadata store, stub `getContainerCreateInfoTable()` to return an in-memory test table, and delegate to either `ContainerSet.newRwContainerSet` or the `ContainerSet` constructor with an injected `Clock`.

State and persistence behavior: No real persistence is used. The in-memory table stands in for container creation metadata, and the provided recovering timeout and optional clock configure runtime container-set behavior.

Dependencies and integration points: `TestBlockDeletingService`, schema compatibility tests, deletion choosing policy tests, stale recovering scrubbing tests, and persistence tests all rely on this helper to construct isolated container sets. The clock overload is important for deterministic stale-recovery tests.

Risks: Because the metadata store is mocked, tests using this helper may not catch bugs in the real witnessed metadata store. The helper must stay aligned with `ContainerSet` constructor and factory signatures.

Test signals: As a helper, its signal comes from downstream tests successfully adding, listing, and timing containers against the returned `ContainerSet`.
