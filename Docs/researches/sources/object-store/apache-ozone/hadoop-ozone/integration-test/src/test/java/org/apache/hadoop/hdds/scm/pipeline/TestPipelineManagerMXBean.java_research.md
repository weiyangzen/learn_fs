<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestPipelineManagerMXBean.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestPipelineManagerMXBean.java

Purpose: Verifies the JMX MXBean view of SCM pipeline state counts.

Important APIs and types: Uses `NonHATests.TestCase`, platform `MBeanServer`, `ObjectName` `Hadoop:service=SCMPipelineManager,name=SCMPipelineManagerInfo`, `TabularData`, `CompositeData`, and `PipelineManager.getPipelineInfo`.

Control flow: The test repeatedly reads the `PipelineInfo` JMX attribute and compares each key/value against the pipeline manager's direct `getPipelineInfo` map until they match or timeout. `getMetricsCount` scans the tabular data for a row whose `key` equals the state string.

State and persistence behavior: No durable state is changed. Runtime pipeline manager state and MXBean-exported state must remain synchronized.

Dependencies and integration points: Covers JMX registration/export for `SCMPipelineManagerInfo` and the conversion of pipeline state counts into open MBean tabular data.

Risks: Three-second timeout is short for slow test environments. The test only verifies states present in the direct map, not extra rows in the MXBean. Values are parsed through `toString`, so MXBean representation changes could break it.

Test signals: All direct pipeline state count entries have matching JMX rows and values within the wait period.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestPipelineManagerMXBean.java -->
