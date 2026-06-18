# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/node/ScmNodeTestUtil.java

Purpose: tiny package-level utility interface for node tests that need to inject a datanode-to-container mapping into an `SCMNodeManager`.

Important APIs and types: static method `setContainers(SCMNodeManager, DatanodeDetails, Set<ContainerID>)` calls `scm.getNodeStateManager().setContainersForTesting(datanode.getID(), containers)`. It can throw `NodeNotFoundException`.

Control flow: no branching; the method is a single delegation to the underlying `NodeStateManager` test hook.

State and persistence: mutates only in-memory node state held by the tested SCM node manager. It does not touch RocksDB or filesystem state.

Integration points and risks: used by tests such as decommission manager and dead-node handler to create known container placement state without going through heartbeats or container reports. The main risk is bypassing production update paths, so tests using it verify downstream behavior from an injected state rather than report ingestion itself.
