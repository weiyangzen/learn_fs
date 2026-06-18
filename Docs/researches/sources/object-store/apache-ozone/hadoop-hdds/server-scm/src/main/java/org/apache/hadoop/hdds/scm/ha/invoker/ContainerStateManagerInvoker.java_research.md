# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/invoker/ContainerStateManagerInvoker.java

Purpose: Generated invoker/proxy for `ContainerStateManager` so container lifecycle mutations are applied through SCM Ratis.

Important APIs and types: Replicated methods are `addContainer`, `removeContainer`, `transitionDeletingOrDeletedToTargetState`, `updateContainerInfo`, and `updateContainerStateWithSequenceId`. The local dispatch also supports reads and replica/container helper updates.

Control flow: Proxy methods for replicated mutations call `invokeReplicateDirect`; read queries and in-memory replica updates call the local implementation. `invokeLocal` resolves overloaded `getContainerInfos` cases by argument count/type, casts protobuf IDs and lifecycle enums, and encodes results where needed.

State and persistence behavior: The invoker itself is stateless. It coordinates mutations that update container state tables and in-memory container state in the real manager.

Dependencies and integration points: Uses protobuf container ids/info, lifecycle enums, pipeline ids, replica sets, table reinitialize hooks, and `ScmCodecFactory` support for these types.

Risks and test signals: Overload disambiguation and generated parameter type arrays are fragile. Tests should cover each replicated method, overloaded list queries, invalid lifecycle transitions, reinitialize pass-through, and that non-replicated replica mutations remain local.
