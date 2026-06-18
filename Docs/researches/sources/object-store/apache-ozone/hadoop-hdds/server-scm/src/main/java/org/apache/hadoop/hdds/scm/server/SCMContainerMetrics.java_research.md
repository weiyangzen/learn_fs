# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/SCMContainerMetrics.java

Purpose: `SCMContainerMetrics` is a Hadoop metrics source that reports counts of containers by lifecycle state and total containers.

Important APIs and types: `create(SCMMXBean)` registers a metrics source named `SCMContainerMetrics`. `getMetrics` reads `scmmxBean.getContainerStateCount()` and emits gauges for open, closing, quasi-closed, closed, deleting, deleted, and total containers. `unRegister` removes the source.

Control flow: During metrics collection, it iterates over all `HddsProtos.LifeCycleState` values to compute total count, then emits selected state gauges using static lifecycle constants.

State and persistence behavior: It has no persistent state. Runtime state is the `SCMMXBean` reference and metrics system registration. Container counts originate from the SCM manager implementing the MXBean.

Dependencies and integration points: It depends on `SCMMXBean`, Hadoop metrics2, `Interns`, and Ozone constants. Operators see the output through SCM metrics sinks.

Risks: The code assumes `getContainerStateCount()` contains non-null entries for every lifecycle state. Adding new lifecycle states changes total calculation but not necessarily individual gauge publication. Re-registration without unregistering can affect tests.

Test signals: Tests should verify gauge names and values, total calculation across all states, behavior when state maps are complete, and unregister behavior.
