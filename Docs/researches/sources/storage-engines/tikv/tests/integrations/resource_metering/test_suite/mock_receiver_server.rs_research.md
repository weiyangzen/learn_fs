# sources/storage-engines/tikv/tests/integrations/resource_metering/test_suite/mock_receiver_server.rs

Purpose: mock resource usage receiver server for tests that validate reporter delivery to a configured receiver address.

Important APIs and functions: `MockReceiverServer::new`, `start_server`, `block`, `unblock`, `shutdown_server`, and `MockReceiverService::report`.

Control flow: `start_server` registers a `ResourceUsageAgent` implementation and starts gRPC. `report` waits while an atomic block flag is true, asynchronously drains all streamed `ResourceUsageRecord`s into a vector, sends the vector over a crossbeam channel, and replies with `EmptyResponse`.

State and persistence: all state is in memory: atomic block flag, received-batch sender, and optional server handle. No persistence.

Dependencies and integration: implements kvproto `ResourceUsageAgent` client-streaming RPC and is controlled by `TestSuite`.

Risks: blocking loop sleeps inside RPC handling and may delay shutdown; `tx.send(...).unwrap()` panics if observers are gone; tests rely on complete stream drain before success.

Test signals: enables receiver tests to observe delivered batches and simulate blocked, invalid, or shut down receivers.
