## sources/object-store/rustfs/crates/targets/tests/amqp_integration.rs

Purpose: ignored integration tests for the AMQP notification target against a RabbitMQ-compatible AMQP 0-9-1 broker.

Important APIs/types/functions: `broker_url` reads `RUSTFS_TEST_AMQP_URL` or defaults to localhost RabbitMQ. `test_args` builds `AMQPArgs` with `amq.topic`, mandatory persistent delivery, empty TLS paths, optional queue settings, and `TargetType::NotifyEvent`. `entity_for` builds event payloads. `bind_queue` declares and binds an exclusive auto-delete queue. `read_one` polls `basic_get` with a 5 second timeout and ACKs the message.

Control flow and state: tests create unique routing keys and queues with UUIDs. Direct publish constructs `AMQPTarget` and calls `save`, then verifies JSON payload and AMQP properties. Reconnect test publishes, closes cached connection, and publishes again. Queue replay test configures `queue_dir`, verifies one queued entry, calls `send_from_store`, verifies delivery, and confirms queue length returns to zero.

Dependencies and integration points: exercises `lapin`, `rustfs_targets::Target`, `check_amqp_broker_available`, `AMQPTarget`, queue store integration, and S3 event shape.

Risks: all tests except none are ignored because they require an external broker. Queue cleanup is manual best-effort. These tests assume default broker exchange behavior and may be sensitive to RabbitMQ availability/timing.

Test signals: provides strong behavioral expectations for broker probing, payload format, persistence flag/content type, reconnect after close, and queue replay deletion, but it is not part of default CI due to `#[ignore]`.
