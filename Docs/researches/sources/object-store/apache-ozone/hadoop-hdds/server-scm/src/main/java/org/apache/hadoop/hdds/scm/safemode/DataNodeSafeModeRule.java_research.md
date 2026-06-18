<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/safemode/DataNodeSafeModeRule.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/safemode/DataNodeSafeModeRule.java

Purpose: `DataNodeSafeModeRule` exits once enough in-service healthy datanodes have registered with SCM.

Important APIs and types: It extends `SafeModeExitRule<NodeRegistrationContainerReport>`, listens to `SCMEvents.NODE_REGISTRATION_CONT_REPORT`, uses `NodeManager`, `NodeStatus.inServiceHealthy`, and tracks `DatanodeID` values in a set.

Control flow: The constructor reads `HDDS_SCM_SAFEMODE_MIN_DATANODE`, sets the threshold metric, and initializes the registration set. `process` adds the reporting datanode ID, updates the count, increments the metric only for first-time registrations, and logs progress. `validate` either uses report-driven count or queries `NodeManager` directly when report processing is disabled.

State and persistence behavior: Runtime state is the registered datanode set and count. No durable state is written. `refresh` is a no-op because the rule does not snapshot SCM DB state.

Dependencies and integration points: It is one of the safe-mode precheck/exit rules built by `SafeModeRuleFactory` and reported by `SCMSafeModeManager`.

Risks: `cleanup` clears the set but not `registeredDns`, so status text after cleanup may retain the old count. Datanode identity uniqueness depends on stable `DatanodeID`. The direct validation path can pass even if registration events were missed.

Test signals: Tests should cover unique registration counting, duplicate report suppression, metric increments, configured threshold, direct node-manager validation path, cleanup behavior, and status text.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/safemode/DataNodeSafeModeRule.java -->
