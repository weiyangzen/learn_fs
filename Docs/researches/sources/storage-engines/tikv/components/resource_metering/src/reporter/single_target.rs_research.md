## sources/storage-engines/tikv/components/resource_metering/src/reporter/single_target.rs

Purpose: implements the default data sink that reports resource usage records to a single configured remote `ResourceUsageAgent` gRPC endpoint.

Important APIs/types/functions: `SingleTargetDataSink`, `Task`, `AddressChangeNotifier`, `Limiter`, `Guard`, and `init_single_target`. Private `DataSinkImpl` schedules incoming batches onto the single-target worker.

Control flow: `update_data_sink` registers or resets the reporter sink based on address. `handle_records` enforces one in-flight report with `Limiter`, lazily builds a grpc client, starts `report_opt` with a two-second timeout, and spawns async sends for each record followed by stream close and response wait.

State/persistence: keeps scheduler, registration guard, grpc environment/client, limiter state, and current address. Address changes clear the client; empty address resets registration.

Dependencies/integration: registered through `DataSinkRegHandle`, uses kvproto `ResourceUsageAgentClient`, grpcio channel/call options, futures `SinkExt`, worker scheduling, and reporting metrics.

Risks: batches are dropped if a previous report is still running, no address is configured, grpc call setup fails, or scheduler enqueue fails. The limiter is released only when the async task drops its guard, so stuck grpc work can block later reports.

Test signals: no direct tests here; reporter tests use mock sinks, while server startup wires this sink into resource metering config.
