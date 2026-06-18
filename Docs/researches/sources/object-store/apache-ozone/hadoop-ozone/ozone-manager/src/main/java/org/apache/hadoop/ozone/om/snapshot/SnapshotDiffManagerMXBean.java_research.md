## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/SnapshotDiffManagerMXBean.java

Purpose: JMX contract for exposing snapshot diff jobs from `SnapshotDiffManager`.

Important APIs and types: declares one method, `List<SnapshotDiffJob> getSnapshotDiffJobs()`, with `@InterfaceAudience.Private`.

Control flow and state: no implementation or persistence; the implementing manager iterates its persistent job table and returns job values.

Dependencies and integration: used by Hadoop `MBeans` registration in `SnapshotDiffManager`, under the `OzoneManager/SnapshotDiffManager` bean name.

Risks and test signals: callers receive all jobs, so large job tables may make JMX reads expensive. Tests should verify MXBean registration delegates to the same job table used by API listing and unregisters on manager close.
