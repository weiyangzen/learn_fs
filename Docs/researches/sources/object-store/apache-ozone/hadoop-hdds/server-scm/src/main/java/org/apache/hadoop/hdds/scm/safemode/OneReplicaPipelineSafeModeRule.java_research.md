<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/safemode/OneReplicaPipelineSafeModeRule.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/safemode/OneReplicaPipelineSafeModeRule.java

Purpose: `OneReplicaPipelineSafeModeRule` requires a configured percentage of pre-existing open Ratis factor THREE pipelines to have at least one datanode report them, ensuring read availability for open containers before safe-mode exit.

Important APIs and types: It extends `SafeModeExitRule<PipelineReportFromDatanode>`, listens to `SCMEvents.PIPELINE_REPORT`, uses `PipelineManager`, `PipelineReport`, `PipelineID`, `RatisReplicationConfig`, and `SafeModeMetrics`.

Control flow: Initialization snapshots current open Ratis THREE pipeline IDs and calculates the threshold. Processing iterates reported pipeline IDs, resolves each pipeline, filters to open Ratis THREE pipelines in the original snapshot, and counts each pipeline only once. When report processing is disabled, validation updates the reported set by scanning open pipelines with non-empty node sets.

State and persistence behavior: Runtime state is the original pipeline ID set, reported pipeline ID set, threshold, and current count. It reads live pipeline state but persists nothing.

Dependencies and integration points: It is part of SCM safe-mode exit and receives pipeline reports from datanode heartbeat dispatch. It complements the healthy-pipeline rule by requiring at least one report for old pipelines.

Risks: It only counts pipelines present during initialization; newly created open pipelines are intentionally excluded until refresh. `cleanup` clears reported IDs but leaves counters and old IDs. Missing pipelines in reports are silently ignored.

Test signals: Tests should cover initial threshold calculation, single counting across duplicate reports, filtering by replication factor and open state, pipeline-not-found tolerance, direct validation path, refresh reset, metrics, and status sample output.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/safemode/OneReplicaPipelineSafeModeRule.java -->
