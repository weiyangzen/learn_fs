## sources/storage-engines/tikv/components/resource_metering/src/reporter/pubsub.rs

Purpose: exposes resource metering records through the `ResourceMeteringPubSub` gRPC streaming API.

Important APIs/types/functions: `PubSubService::new`, `impl ResourceMeteringPubSub for PubSubService`, and private `DataSinkImpl`. `subscribe` registers a bounded channel-backed sink and spawns an async task to forward record batches to the streaming response.

Control flow: on subscription, a channel of capacity 1 is created. Reporter calls `DataSinkImpl::try_send`; the gRPC task receives batches, records metrics, sends each `ResourceUsageRecord`, and exits on channel close or send error. The registration guard lives inside the async task, deregistering when the stream ends.

State/persistence: per-subscriber in-memory bounded channel and guard. No replay or durable storage.

Dependencies/integration: integrates kvproto pubsub service, grpcio server streaming, futures mpsc, `DataSinkRegHandle`, `DataSink`, and report/ignored/duration metrics.

Risks: backpressure drops whole batches because the channel capacity is one; slow or broken subscribers terminate their stream; each record is cloned before send.

Test signals: no direct tests in this file; behavior is indirectly covered through reporter/data-sink abstractions.
