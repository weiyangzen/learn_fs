# sources/storage-engines/tikv/tests/integrations/resource_metering/test_suite/mod.rs

Purpose: shared resource metering integration harness. It creates temporary storage, recorder/reporter workers, pubsub and receiver endpoints, dynamic config controls, workload generation, and record collection utilities.

Important APIs and functions: `TestSuite` owns pubsub port, optional receiver server, storage, `ConfigController`, `ResourceTagFactory`, channels, gRPC env, Tokio runtime, workload cancellation channels, temp dir, and worker shutdown closure. Key methods include `new`, `get_storage`, `get_tag_factory`, `subscribe`, config setters, receiver controls, `setup_workload`, `cancel_workload`, `nonblock_receiver_all`, `block_receive_one`, `merge_records`, `flush_receiver`, and `Drop`.

Control flow: `new` initializes recorder, reporter, single-target worker, mock pubsub server, config manager, test storage, channel, and runtime. `setup_workload` spawns a loop that performs tagged storage `get`s for each tag until a oneshot cancellation fires. Receiver/pubsub helpers expose the emitted records to tests.

State and persistence: uses a temporary TiKV config directory and Rocks storage; recorder/reporter workers maintain in-memory accounting; dynamic config changes flow through `ConfigController`; drop shuts down pubsub, single-target, reporter, and recorder workers.

Dependencies and integration: `resource_metering::{init_recorder, init_reporter, init_single_target, ConfigManager}`, TiKV storage builders, `MockLockManager`, gRPC clients/servers, crossbeam channels, futures, and Tokio runtime.

Risks: `Drop` unwraps `stop_workers`; workload loops need cancellation or runtime teardown; `flush_receiver` depends on report interval plus a timing cushion.

Test signals: all resource metering integration tests depend on this harness for reliable worker startup, dynamic config updates, record delivery, and cleanup.
