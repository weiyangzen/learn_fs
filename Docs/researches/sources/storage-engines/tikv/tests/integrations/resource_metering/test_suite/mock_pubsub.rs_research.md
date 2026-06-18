# sources/storage-engines/tikv/tests/integrations/resource_metering/test_suite/mock_pubsub.rs

Purpose: helper that builds a mock gRPC pubsub server for resource metering tests.

Important APIs and functions: `MockPubSubServer::new(port, env, reg_handle) -> Server`, `PubSubService::new`, and `create_resource_metering_pub_sub`.

Control flow: constructs gRPC channel args with two concurrent streams and unlimited message sizes, creates a `PubSubService` over the data sink registry, binds `127.0.0.1:port`, registers the generated service, and returns the unstarted server.

State and persistence: holds only server runtime state and the data sink registry handle; no disk persistence.

Dependencies and integration: connects `resource_metering::DataSinkRegHandle`/`PubSubService` to kvproto's resource metering pubsub service consumed by `TestSuite::subscribe`.

Risks: assumes localhost and a free port; stream limit may need adjustment if subscriber counts grow.

Test signals: indirect signal through pubsub tests successfully connecting and receiving records.
