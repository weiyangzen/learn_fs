# sources/storage-engines/tikv/tests/integrations/resource_metering/test_pubsub.rs

Purpose: tests resource metering pubsub delivery to one and multiple subscribers.

Important APIs and functions: `TestSuite::new`, `setup_workload`, `subscribe`, `StreamExt::take/map/collect`, and `ResourceUsageRecord` tag extraction.

Control flow: `test_basic` starts workload for `req-1` and `req-2`, subscribes once, collects four records, and requires both tags. `test_multiple_subscribers` creates three subscriptions, spawns collectors on the suite runtime, and requires each subscriber to observe both tags.

State and persistence: state is in pubsub streams, data sink registry, and resource metering worker buffers. Temporary storage only drives workload generation.

Dependencies and integration: `resource_metering::PubSubService`, mock pubsub server, gRPC streaming, and shared test suite.

Risks: assumes four records are enough to see both tags; multiple subscribers exercise stream fan-out and registration concurrency.

Test signals: confirms external pubsub streams receive tagged usage records and fan out to multiple subscribers.
