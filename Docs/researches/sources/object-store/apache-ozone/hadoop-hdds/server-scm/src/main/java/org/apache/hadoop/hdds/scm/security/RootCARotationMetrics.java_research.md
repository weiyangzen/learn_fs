# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/security/RootCARotationMetrics.java

Purpose: `RootCARotationMetrics` publishes counters and timing for SCM root CA rotation attempts. It lets operators distinguish total rotation attempts, successful rotations, and duration of the last successful rotation.

Important APIs and types: `create()` registers the source with `DefaultMetricsSystem` under `RootCARotationMetrics.NAME`. Public mutators are `incrTotalRotationNum`, `incrSuccessRotationNum`, and `setSuccessTimeInNs`. Public readers expose total and successful rotation counts. `unRegister()` removes the metrics source.

Control flow: `RootCARotationManager` increments total attempts when scheduling a rotation and increments success plus duration after all SCMs acknowledge and commit. There is no failure counter; failed attempts are inferred from total minus success.

State and persistence behavior: Metrics are in-memory Hadoop metrics primitives and are not persisted. A process restart resets them.

Dependencies and integration points: It uses Hadoop metrics2 annotations and mutable metric classes. The class is created in the rotation manager constructor and unregistered on manager stop.

Risks: The private `ms` field is stored but not used after construction. Re-registering without unregistering can collide in tests. The lack of explicit failure and timeout counters limits diagnosis of repeated rotation failures.

Test signals: Tests should verify registration name, counter increments, last success time gauge, unregister behavior, and total-minus-success interpretation on failed rotation scenarios.
