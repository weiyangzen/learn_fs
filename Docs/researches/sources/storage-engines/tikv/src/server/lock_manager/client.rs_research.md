# sources/storage-engines/tikv/src/server/lock_manager/client.rs

Purpose: deadlock detector follower-side gRPC client wrapper for the bidirectional `Detect` stream to the current detector leader.

Important APIs/types/functions: `env()` builds the shared gRPC environment; `Client::new` creates a `DeadlockClient` channel through `SecurityManager`; `register_detect_handler` creates send/receive futures for the streaming RPC; `detect` enqueues `DeadlockRequest`s onto the unbounded sender. `Callback` handles `DeadlockResponse`.

Control flow: after construction, `register_detect_handler` opens the `detect` stream, stores an unbounded request sender, creates a send task that forwards channel items to gRPC with default write flags, and creates a receive task that invokes the callback for each response. `detect` pushes requests into the sender and converts send failure into lock-manager `Error`.

State and persistence: client state is only the gRPC stub and optional stream sender. It persists no lock state; the detector leader owns the graph.

Dependencies and integration: depends on `kvproto::deadlock`, `grpcio`, futures mpsc, TiKV security, and the detector thread name prefix. `deadlock.rs` uses this client when a follower forwards local wait-for events to the leader.

Risks: `register_detect_handler` and `detect` use `unwrap` on stream creation and sender presence, so callers must follow lifecycle ordering and handle stream creation assumptions. The unbounded channel can grow if the network stream stalls. Send task cancellation closes the gRPC sink.

Test signals: tested indirectly by detector tests and production stream wiring; no standalone tests in this file.
