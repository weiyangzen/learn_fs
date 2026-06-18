# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/invoker/ScmInvoker.java

Purpose: Base class for generated non-reflection SCM HA invokers, providing proxy construction, Ratis request submission, and exception translation.

Important APIs and types: Stores the real implementation, proxy, and `SCMRatisServer`. Exposes `getType`, `getApi`, `getImpl`, `getProxy`, abstract `invokeLocal`, `invokeReplicateDirect`, `invokeReplicateClient`, and `translateException`. Inner `NameAndParameterTypes` supplies method names and declared parameter types.

Control flow: Direct replication submits `SCMRatisRequest` through the local Ratis server. Client replication encodes the request and sends it through `HASecurityUtils.submitScmRequestToRatis`. Both decode `SCMRatisResponse` and translate errors to `SCMException`.

State and persistence behavior: Stateless with respect to DB; it is the replication transport boundary for persistent mutations owned by implementations.

Dependencies and integration points: All generated invokers extend it; `SCMRatisServer.getProxyHandler` registers them with `SCMStateMachine`.

Risks and test signals: Exception mapping controls client-visible error codes for timeout, not-leader, IO, and internal failures. Tests should cover nested `ExecutionException`/`InvocationTargetException`, existing `SCMException` preservation, direct versus client submission, and missing invoker handling in the state machine.
