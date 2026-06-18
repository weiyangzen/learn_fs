<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestReplicationAnnotation.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestReplicationAnnotation.java

Purpose: This test verifies that methods annotated for SCM Ratis replication are routed through the `SCMRatisServer` proxy submission path rather than invoked directly.

Important APIs and types: It uses an inline `SCMRatisServer` implementation, `SCMRatisServer.getProxyHandler`, `ContainerStateManagerInvoker`, `ContainerStateManager`, `SCMRatisRequest`, `SCMRatisResponse`, and `RequestType.CONTAINER`.

Control flow: Setup creates a minimal `SCMRatisServer` whose `submitRequest` always throws an `IOException` with a known message. The test wraps a mocked `ContainerStateManager` in a generated invoker/proxy, calls `addContainer`, and asserts the thrown exception contains the proxy-submission marker.

State and persistence behavior: There is no persistence. Runtime state is the proxy, mocked manager type, and thrown exception.

Dependencies and integration points: This guards annotation-driven HA replication plumbing for SCM metadata managers. It confirms the proxy path captures method calls and sends them to Ratis.

Risks: The test only checks one replicated method and uses a stub server; it does not validate serialized arguments or Raft execution.

Test signals: `addContainer` throws the known `submitRequest is called` IOException, proving the proxy intercepted the annotated method.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestReplicationAnnotation.java -->
