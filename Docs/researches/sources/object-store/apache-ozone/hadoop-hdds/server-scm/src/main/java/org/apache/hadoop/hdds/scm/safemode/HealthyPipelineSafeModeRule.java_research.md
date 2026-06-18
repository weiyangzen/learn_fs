<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/safemode/HealthyPipelineSafeModeRule.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/safemode/HealthyPipelineSafeModeRule.java

Purpose: `HealthyPipelineSafeModeRule` requires enough open Ratis factor THREE pipelines to be healthy before SCM exits safe mode, allowing write traffic to resume safely.

Important APIs and types: It extends `SafeModeExitRule<Pipeline>`, listens for `SCMEvents.OPEN_PIPELINE`, and uses `PipelineManager`, `NodeManager`, `SCMContext`, `FinalizationManager`, `RatisReplicationConfig`, `NodeStatus`, and `SafeModeMetrics`.

Control flow: Initialization snapshots open Ratis THREE pipelines and sets a threshold as the max of configured percentage and a minimum derived from min datanodes divided by three. Event processing ignores non-Ratis/THREE pipelines, duplicates, wrong node counts, and pipelines whose datanodes are missing or not in-service healthy; valid pipelines increment counters and leave the unprocessed set. Validation bypasses the rule during upgrade finalization when new pipelines should not be created, otherwise either checks event counters or queries the pipeline manager directly.

State and persistence behavior: Runtime state includes threshold count, current healthy count, processed IDs, and unprocessed IDs. The rule reads live pipeline and node state but writes only metrics and logs.

Dependencies and integration points: It is coordinated by `SCMSafeModeManager`, depends on pipeline open events from pipeline management, and gates SCM service startup behavior through safe-mode status.

Risks: The event-driven path requires all three pipeline nodes to be present in the pipeline object and healthy at processing time. Thresholds can change during refresh as open pipeline counts change. It balances safety with upgrade finalization by bypassing when pipeline creation is intentionally disabled.

Test signals: Tests should cover threshold math, finalization bypass, non-Ratis and non-THREE skipping, duplicate reports, unhealthy/missing datanode rejection, direct validation path, refresh behavior, metrics, and status samples.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/safemode/HealthyPipelineSafeModeRule.java -->
