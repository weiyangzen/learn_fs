# sources/object-store/rustfs/crates/targets/Cargo.toml

## Purpose
Defines `rustfs-targets`, the notification/audit target abstraction and implementation crate.

## Dependencies and Integration
The manifest pulls in configuration, extension schema, TLS runtime, S3 types, async traits, network clients for AMQP, NATS, Pulsar, MQTT, Redis, Kafka, MySQL, PostgreSQL, HTTP/webhook, rustls/native certs, queue/serialization utilities, metrics, `arc-swap`, `parking_lot`, and Tokio. Dev dependencies include Criterion and tempfile. It declares the `queue_store_benchmark` Criterion bench.

## Risks and Test Signals
This is a broad integration crate with many optional-looking but direct dependencies, so build times and supply-chain surface are significant. The bench target focuses on queue-store raw read/write performance with and without compression. Workspace lints apply.
