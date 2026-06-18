# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/safemode/SafeModeRuleFactory.java

Purpose: `SafeModeRuleFactory` is the singleton factory that wires SCM safe mode exit rules to configuration, managers, SCM context, and the event queue. It centralizes the current manual list of safe mode rules used during SCM startup.

Important APIs and types: `initialize(...)` installs the singleton with `ConfigurationSource`, `SCMContext`, `EventQueue`, `PipelineManager`, `ContainerManager`, and `NodeManager`. `getInstance()` returns the initialized singleton or throws. `addSafeModeManager()` calls `loadRules()`. Accessors expose all safe mode rules, pre-check rules, and a typed `getSafeModeRule(Class<T>)`.

Control flow: `loadRules` always creates `RatisContainerSafeModeRule`, `ECContainerSafeModeRule`, and `DataNodeSafeModeRule`. The datanode rule is also added to `preCheckRules`. If `scmContext.getScm()` is a real `StorageContainerManager` with a Ratis server, it adds `StateMachineReadyRule`. If a `PipelineManager` exists, it adds healthy-pipeline and one-replica-pipeline rules.

State and persistence behavior: The factory stores rule instances in memory and does not persist rule configuration. Rule state is held by the individual rule objects. Re-initialization replaces the singleton and starts a fresh rule list.

Dependencies and integration points: It binds safe mode to container, EC container, datanode, pipeline, HA/Ratis state-machine readiness, and the event bus. The implementation notes a future annotation-based discovery replacement.

Risks: The singleton is process-global, which creates test isolation and reconfiguration risk. `loadRules` appends to existing lists, so repeated `addSafeModeManager` calls on the same instance can duplicate rules. The HA state-machine rule is only added for concrete `StorageContainerManager`, so Recon/passive SCM variants can intentionally differ.

Test signals: Tests should verify initialization guard behavior, rule ordering, pre-check contents, optional pipeline rules, optional HA state-machine rule, and no unintended duplicate registration in repeated initialization scenarios.
