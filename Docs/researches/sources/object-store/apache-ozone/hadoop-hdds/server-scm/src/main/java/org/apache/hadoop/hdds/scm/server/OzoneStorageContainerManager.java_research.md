# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/OzoneStorageContainerManager.java

Purpose: This interface is the facade contract for SCM-like services. It lets passive SCM variants such as Recon reuse server/protocol code while swapping selected manager implementations.

Important APIs and types: The interface exposes lifecycle methods `start`, `stop`, `join`, and `shutDown`, plus accessors for node, block, pipeline, container, replication, balancer, datanode RPC address, SCM node details, reconfiguration handler, metadata store, HA manager, and sequence ID generator.

Control flow: There is no implementation here. Protocol servers and dispatchers call this facade to reach managers without depending directly on the concrete `StorageContainerManager` in every path.

State and persistence behavior: The interface owns no state. Implementations provide access to persistent metadata stores, HA state, sequence IDs, and manager state.

Dependencies and integration points: It is consumed by `SCMDatanodeProtocolServer`, `SCMDatanodeHeartbeatDispatcher`, and other server-side classes that need SCM services but should remain overrideable for Recon.

Risks: The facade still exposes many concrete manager types, so alternate implementations must satisfy a broad surface. Methods do not encode nullability or readiness, so callers must know which managers are valid for passive modes.

Test signals: Tests for passive SCM variants should verify protocol servers can operate with custom implementations and that unsupported managers fail deliberately rather than by accidental null dereference.
