<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestNode2PipelineMap.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestNode2PipelineMap.java

Purpose: Tests the consistency of mappings from pipeline to open containers and from datanode to pipelines.

Important APIs and types: Uses `NonHATests.TestCase`, `StorageContainerManager`, `ContainerManager`, `PipelineManager`, `ContainerWithPipeline`, `ContainerInfo`, `ContainerID`, `PipelineID`, `DatanodeDetails`, `LifeCycleEvent`, and Ratis three replication config.

Control flow: Setup allocates a Ratis three container and resolves its pipeline. The test fetches containers in that pipeline, verifies the allocated container is present, queries a datanode's pipelines, closes the container through `FINALIZE` and `CLOSE`, verifies the pipeline's open-container set shrinks, then closes and deletes the pipeline and checks datanode mappings no longer contain it.

State and persistence behavior: Runtime SCM maps are the target: pipeline-to-open-container set and node-to-pipeline set. Container lifecycle transitions update whether a container is considered in-pipeline.

Dependencies and integration points: Integrates container lifecycle management, pipeline manager deletion, and SCM node manager pipeline membership tracking.

Risks: The test assumes the allocated pipeline has exactly three nodes and that no unrelated open-container changes affect the initial set except the tested container. It is abstract and relies on the non-HA fixture implementation.

Test signals: Signals include allocated container ID present in pipeline set, datanode pipeline set containing the pipeline ID, pipeline container count decreasing by one after close, and datanode pipeline set excluding the ID after pipeline delete.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestNode2PipelineMap.java -->
