<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/conf/ReconfigurationChangeCallback.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/conf/ReconfigurationChangeCallback.java

## Purpose
`ReconfigurationChangeCallback` is a functional interface for code that wants to react to configuration property changes.

## Important APIs, Types, and Functions
It declares one method: `onPropertiesChanged(Map<String, Boolean> changedKeys, Configuration newConf)`.

## Control Flow
There is no implementation flow in the interface. Callers provide lambdas or classes that receive changed-key metadata and the new configuration.

## State and Persistence Behavior
No state is owned by the interface.

## Dependencies and Integration Points
It depends on Hadoop `Configuration` and integrates with reconfiguration handlers/callback consumers elsewhere in HDDS.

## Risks and Test Signals
Risks include ambiguous Boolean semantics in `changedKeys` unless documented by callers and callback exceptions affecting reconfiguration code if not isolated. Test signals should cover callback invocation with expected changed-key maps and exception handling by the caller.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/conf/ReconfigurationChangeCallback.java -->
