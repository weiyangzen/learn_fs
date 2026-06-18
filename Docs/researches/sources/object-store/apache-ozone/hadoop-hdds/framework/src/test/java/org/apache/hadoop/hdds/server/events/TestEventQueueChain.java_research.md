<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/events/TestEventQueueChain.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/events/TestEventQueueChain.java

Purpose: demonstrates and tests chained event publication where one handler publishes a follow-up event consumed by another handler.

Important APIs/types/functions: `EventQueue`, `TypedEvent<FailedNode>`, `EventHandler<FailedNode>`, `EventPublisher.fireEvent`, `PipelineManager`, `NodeWatcher`, and `processAll`.

Control flow: registers `PipelineManager` on `DECOMMISSION` and `NodeWatcher` on `DECOMMISSION_START`, fires a `FailedNode`, and drains the queue. `PipelineManager.onMessage` emits the follow-up event; `NodeWatcher.onMessage` is the terminal consumer.

State and persistence behavior: no durable state. The only payload state is `FailedNode.nodeId`, and queue state is transient.

Dependencies and integration points: validates that event handlers can use the supplied `EventPublisher` to enqueue additional work in the same `EventQueue`.

Risks: this test currently has no explicit assertions; it primarily detects exceptions or deadlocks during chained processing. Stronger test signals would record terminal handler receipt.

Test signals: implicit success is no exception and timely `processAll` completion after chained publish.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/events/TestEventQueueChain.java -->
