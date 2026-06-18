# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/logs/container/ListContainers.java

Purpose: `ListContainers` queries parsed container-log data by lifecycle or supported health state.

Important APIs and types: It extends `AbstractSubcommand`, uses picocli `@ArgGroup(multiplicity = "1")` for mutually exclusive lifecycle/health selection, `ListLimitOptions`, `HddsProtos.LifeCycleState`, `ContainerHealthState`, and `ContainerDatanodeDatabase`.

Control flow: The command resolves the DB path, builds a database helper, and dispatches based on the chosen exclusive option. Lifecycle state calls `listContainersByState`; health state supports UNDER_REPLICATED and OVER_REPLICATED through `listReplicatedContainers`, UNHEALTHY through `listUnhealthyContainers`, and QUASI_CLOSED_STUCK through `listQuasiClosedStuckContainers`.

State and persistence behavior: It reads SQLite tables produced by the parser. No writes occur.

Dependencies and integration points: It exposes database analysis routines through CLI flags and uses common Ozone list-limit handling.

Risks: Unsupported health states print an error but do not fail. Exactly one selector is required by picocli, so command usability depends on arg group parsing.

Test signals: Correct database helper method for each state category, limit propagation, and unsupported health state message.
