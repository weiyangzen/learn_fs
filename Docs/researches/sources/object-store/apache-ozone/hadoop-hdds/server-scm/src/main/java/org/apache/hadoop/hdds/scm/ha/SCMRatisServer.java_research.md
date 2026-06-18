# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMRatisServer.java

Purpose: Abstraction over the SCM Ratis server used by managers and generated proxies to submit replicated requests, manage snapshots, inspect roles, and change membership.

Important APIs and types: Defines `start`, `stop`, `isStopped`, `submitRequest`, `triggerSnapshot`, `registerStateMachineHandler`, `getDivision`, `getRatisRoles`, `triggerNotLeaderException`, `addSCM`, `removeSCM`, `getSCMStateMachine`, `getGrpcTlsConfig`, and `getLeaderId`. Default `getProxyHandler` registers an invoker and returns its proxy.

Control flow: Implementations register `ScmInvoker` handlers before replicated APIs are used. Proxies submit `SCMRatisRequest` values and receive `SCMRatisResponse` values.

State and persistence behavior: State belongs to implementations: Ratis log, state machine, membership, TLS config, and snapshot index.

Dependencies and integration points: Central boundary between SCM services, generated invokers, Ratis, and HA membership commands.

Risks and test signals: `getProxyHandler` registration order is required for local apply success. Tests should cover request submission, not-leader exception content, snapshot trigger result, role rendering, membership reconfiguration, and TLS config propagation.
