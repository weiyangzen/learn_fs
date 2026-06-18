## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/resources/ozone-site.xml

Purpose: Test resource configuration overriding selected datanode storage behavior for container-service tests.

Important APIs/types/functions: XML Hadoop/Ozone configuration with properties `hdds.datanode.du.factory.classname` and `hdds.datanode.volume.min.free.space`.

Control flow: Loaded by test configuration mechanisms as a site override. It sets disk usage factory to `org.apache.hadoop.hdds.fs.MockSpaceUsageCheckFactory$None` and minimum free space to `0MB`.

State and persistence behavior: No runtime state itself; affects tests by disabling real disk usage checks and free-space floor constraints.

Dependencies and integration points: Integrates with Hadoop configuration loading and Ozone datanode volume space accounting.

Risks and test signals: Useful for deterministic tests, but it can hide production-like disk-space behavior if tests unintentionally rely on this resource.
