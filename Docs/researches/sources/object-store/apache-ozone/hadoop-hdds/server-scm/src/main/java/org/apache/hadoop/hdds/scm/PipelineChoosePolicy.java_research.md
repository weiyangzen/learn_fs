# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/PipelineChoosePolicy.java

Purpose: Strategy interface for choosing an existing pipeline from candidate pipelines.

Important APIs and types: Defines `init(NodeManager)`, `choosePipeline(List<Pipeline>, PipelineRequestInformation)`, and default `choosePipelineIndex`.

Control flow: Implementations may initialize with `NodeManager`, choose a pipeline object, and optionally expose the chosen list index. The default index returns `-1` for null/empty lists and `0` otherwise.

State and persistence behavior: Stateless interface; implementations may keep policy state after initialization.

Dependencies and integration points: Used by SCM pipeline allocation and selection code with request metadata.

Risks: Default `choosePipelineIndex` may not match custom `choosePipeline` implementations unless overridden.

Test signals: Implementation tests should verify initialization, empty-list handling, and pipeline/index consistency.
