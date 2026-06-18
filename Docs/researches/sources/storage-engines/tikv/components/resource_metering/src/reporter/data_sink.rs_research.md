## sources/storage-engines/tikv/components/resource_metering/src/reporter/data_sink.rs

Purpose: defines the output abstraction for sending aggregated resource usage records to a remote or local consumer.

Important APIs/types/functions: `DataSink: Send` with `try_send(&mut self, Arc<Vec<ResourceUsageRecord>>) -> Result<()>`.

Control flow: reporter upload methods call `try_send` for each registered sink. Implementations decide whether to enqueue, stream, or fail the batch.

State/persistence: trait has no state; implementations hold queues, schedulers, grpc clients, or streams. Calls are best-effort and errors are handled by callers with logging/metrics.

Dependencies/integration: depends on `kvproto::resource_usage_agent::ResourceUsageRecord` and crate error `Result`. Implemented by pubsub and single-target sinks.

Risks: the interface has no async completion or retry contract; `try_send` failure means caller-side drop. Mutable access serializes per-sink sends inside the reporter worker.

Test signals: summary and reporter tests define mock `DataSink` implementations to validate reporting behavior.
