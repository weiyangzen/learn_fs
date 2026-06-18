# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/FaultInjector.java

Purpose: `FaultInjector` is a testing hook base class for injecting pauses, exceptions, and container command types into Ozone workflows.

Important APIs/types/functions: visible-for-testing methods include `init()`, `pause()`, `resume()`, `reset()`, `setException(Throwable)`, `getException()`, `setType(ContainerProtos.Type)`, and `getType()`. The base implementation is no-op/null-returning.

Control flow: production code can hold a `FaultInjector` reference defaulting to this no-op base, while tests install subclasses that block, throw, or record state at specific injection points.

State and persistence: base class has no state. Test subclasses usually keep exception/type/latch state in memory.

Dependencies/integration: depends on container protobuf command type. Used by disk balancer, key/container operations, lease recovery, snapshot transfer, and other fault-injection tests.

Risks: injection hooks must be carefully reset after tests to avoid cross-test contamination. No-op defaults make production safe, but broad visible-for-testing methods can hide unused or stale injection points.

Test signals: disk balancer tests define custom subclasses; lease recovery and OM Ratis snapshot transfer tests use `FaultInjectorImpl` to simulate failures and pauses.
