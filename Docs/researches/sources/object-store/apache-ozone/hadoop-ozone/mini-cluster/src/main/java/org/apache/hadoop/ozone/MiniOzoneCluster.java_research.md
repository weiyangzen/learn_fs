# sources/object-store/apache-ozone/hadoop-ozone/mini-cluster/src/main/java/org/apache/hadoop/ozone/MiniOzoneCluster.java

Purpose: Public test-harness interface and builder base for creating and controlling in-process Ozone clusters.

Important APIs/types/functions: Static factories `newBuilder` and `newHABuilder`; cluster accessors for config, SCM, OM, datanodes, client, SCM location client, cluster id/name/base dir; readiness waits; restart/shutdown operations for SCM, OM, and datanodes; start/stop lifecycle. Nested `Builder` configures cluster id/path, SCM configurator, datanode count/start flag, certificate/secret clients, datanode factory, and extra services. Nested `DatanodeFactory` and `Service` allow customization.

Control flow, state, and persistence: The builder creates unique cluster ids and temporary paths under `test.build.data` or `target/test/data`. `prepareForNextBuild()` clones configuration and unsets directories/HTTP base paths so the same builder can create multiple isolated clusters. Cluster lifecycle methods control in-process services and temp storage cleanup.

Dependencies and integration points: Integrates with `MiniOzoneClusterImpl`, `MiniOzoneHAClusterImpl`, OM, SCM, datanode service, Ozone client factory, Hadoop/Ozone configuration keys, certificate/secret clients, and Ratis `ExitUtils` to disable system exit in tests.

Risks: Builders are stateful and reused by provider code; missing cleanup of config keys can make clusters share directories. Datanode count zero disables SCM safemode, which is correct for fast tests but changes behavior. Callers own clients returned by `newClient()` and must close or rely on cluster shutdown.

Test signals: Downstream integration tests use this interface directly. No direct unit test in this subset.
