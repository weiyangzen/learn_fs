# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestCreateForReadComparator.java

Purpose: tests `ECPipelineProvider.CREATE_FOR_READ_COMPARATOR`, which orders replica datanodes when building EC read pipelines.

Important APIs and types: uses `Comparator<NodeStatus>`, `NodeStatus`, `NodeOperationalState`, and `NodeState`.

Control flow: parameterized `readOnly` verifies healthy and healthy-readonly compare as equal for every operational state. `healthyFirst` asserts healthy statuses sort before stale/dead statuses, including maintenance/decommissioning healthy states. `inServiceFirst` asserts in-service healthy sorts ahead of decommissioning or entering-maintenance healthy nodes.

State and persistence behavior: none; tests compare immutable status values.

Dependencies and integration points: directly protects EC read pipeline node ordering used by `ECPipelineProvider.createForRead`.

Risks and edge cases: comparator ordering is tested by sign only, not full stable order. Equal treatment of read-only health states is intentional and important for read-path inclusion.

Test signals: focused regression signal that EC read pipelines prefer in-service healthy nodes, then other healthy operational states, then stale/dead nodes.
