# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/ErrorInjector.java

Purpose: Functional test hook for injecting server-like errors into client-side Ratis request handling.

Important APIs/types/functions: Single method `getResponse(ContainerCommandRequestProto request, ClientId id, Pipeline pipeline)` returns a `RaftClientReply` to substitute for a real Ratis response, or presumably null to allow normal execution.

Control flow: `XceiverClientCreator.enableErrorInjection` stores an injector, and `XceiverClientRatis.sendRequestAsync` consults it before sending a request to Ratis. A non-null reply short-circuits normal network IO with a completed future.

State and persistence behavior: Interface has no state. The global static reference in `XceiverClientCreator` is the stateful integration point.

Dependencies and integration points: Depends on container command protobufs, Ratis client IDs/replies, and SCM pipelines. Used by tests or fault-injection scenarios.

Risks: Global static injection can leak between tests if not reset. Injected replies must be coherent with request and pipeline or downstream code can fail in surprising ways.

Test signals: Fault-injection tests should assert injected failures propagate and normal path resumes when injector returns null or is cleared.
