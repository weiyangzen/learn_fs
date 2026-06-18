# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/invoker/PipelineStateManagerInvoker.java

Purpose: Generated HA invoker/proxy for `PipelineStateManager` pipeline table and lifecycle mutations.

Important APIs and types: Replicated methods are `addPipeline`, `removePipeline`, and `updatePipelineState`. Local dispatch covers container membership in pipelines, query methods, counts, `close`, and `reinitialize`.

Control flow: Proxy write methods submit direct Ratis requests using protobuf pipeline ids/states. Read/query methods call the local implementation. `invokeLocal` handles overloaded `getPipelines` variants and encodes returned `Pipeline`, collection, count, or void responses.

State and persistence behavior: The underlying manager updates the pipeline table and in-memory pipeline state. The invoker has no persistence but defines what crosses the replicated boundary.

Dependencies and integration points: Used by pipeline manager, Ratis state machine, pipeline codecs, and checkpoint reload.

Risks and test signals: Query overload selection and generated parameter arrays are compatibility-sensitive. Tests should cover duplicate/not-found/invalid-state exceptions, replicated add/remove/update, reinitialize table swap, local container membership operations, and list serialization.
