# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMHAManagerStub.java

Purpose: Lightweight HA manager for Recon and tests that simulates Ratis submission and leader/follower behavior without running a real Raft server.

Important APIs and types: Static factories create leader/follower instances and optionally wrap a `DBStore` in `SCMHADBTransactionBufferStub`. Inner `RatisServerStub` implements `SCMRatisServer`, stores `ScmInvoker` handlers by `RequestType`, and exposes `submitRequest`, `triggerNotLeaderException`, and fixed role strings.

Control flow: On leader mode, `submitRequest` decodes the requested invoker and calls `invokeLocal`, wrapping success or `StateMachineException` in a synthetic `RaftClientReply`. On follower mode, it returns a `NotLeaderException`.

State and persistence behavior: Persists only through the supplied transaction buffer. Snapshot provider, checkpoint download/install, add/remove SCM, and real Ratis division/state machine paths are intentionally no-ops or null.

Dependencies and integration points: Used by components that build HA proxies through `getProxyHandler` but need deterministic local execution in unit tests or Recon.

Risks and test signals: Null `getDivision` and `getSCMStateMachine` make it unsuitable for code paths that need real Raft metadata. Tests can assert leader local invocation, follower not-leader translation, invoker registration, and buffer close behavior.
