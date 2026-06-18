# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/freon/TestFreonWithPipelineDestroy.java

Purpose: Freon integration test verifying RandomKeyGenerator can write successfully before and after an active Ratis pipeline is closed/destroyed and a new pipeline becomes ready.

Important APIs, types, and functions: Uses `MiniOzoneCluster`, `RandomKeyGenerator`, Ratis timeout configs, `XceiverServerSpi.getPipelineReport`, `PipelineID`, `PipelineManager`, and picocli `CommandLine`. Helpers are `startFreon` and `destroyPipeline`.

Control flow: Setup configures short pipeline destroy timeout, pipeline report interval, heartbeat processing, Ratis timeouts, and starts a three-datanode cluster. The test runs one validated 20 MB Freon write, closes the pipeline reported by datanode 0 through SCM `PipelineManager.closePipeline`, waits for a new Ratis THREE pipeline, then runs the same Freon write again.

State and persistence behavior: Freon writes persistent replicated data. Closing a pipeline changes SCM pipeline state and datanode pipeline reports. New pipeline readiness is required before the second write.

Dependencies and integration points: Exercises Freon object writes, SCM pipeline manager, datanode pipeline reports, Ratis pipeline recreation, and validation after topology disruption.

Risks: Pipeline report ordering assumes the first report is suitable. Pipeline closure and recreation are asynchronous and can be timing-sensitive. Freon uses generic object names, so repeated runs rely on generator uniqueness or clean cluster state.

Test signals: Both Freon runs must create exactly one volume, one bucket, one key, and zero failed validations; cluster must provide a ready Ratis THREE pipeline after closure.
