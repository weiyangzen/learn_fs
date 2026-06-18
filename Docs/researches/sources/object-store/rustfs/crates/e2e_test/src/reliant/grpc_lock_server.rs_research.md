# sources/object-store/rustfs/crates/e2e_test/src/reliant/grpc_lock_server.rs

## sources/object-store/rustfs/crates/e2e_test/src/reliant/grpc_lock_server.rs

Purpose: a minimal tonic `NodeService` implementation for lock tests. It exposes only ping and lock-related RPCs backed by an injected `Arc<dyn LockClient>`, while every unrelated storage/admin RPC returns `Status::unimplemented("lock-only test server")`.

Important APIs and types: `ResponseStream<T>` is the stream type required by generated service methods. `lock_result_from_response`, `lock_result_from_error`, and `lock_result_from_release` normalize `rustfs_lock::LockResponse` or booleans into protobuf `GenerallyLockResult`. `MinimalLockNodeService` owns a lock client and implements `node_service_server::NodeService`. `spawn_lock_server` binds `127.0.0.1:0`, wraps the service in `NodeServiceServer`, serves a `TcpListenerStream`, and returns an HTTP endpoint string plus Tokio task handle.

Control flow: `ping` returns a flatbuffer payload containing `pong`. `lock`, `un_lock`, `force_un_lock`, and `refresh` decode JSON `LockRequest` from `GenerallyLockRequest.args`, call the corresponding `LockClient` method, and return a `GenerallyLockResponse` with success, error text, and optional serialized `LockInfo`. Decode failures are represented as successful gRPC responses with `success=false` rather than tonic errors. `lock_batch` and `un_lock_batch` prefill per-input failure results, decode valid JSON entries, call batch trait methods once for valid requests, then map batch results back to original indices.

State and persistence: server state is delegated entirely to the injected `LockClient`, normally a `LocalClient` with a `GlobalLockManager` or a test `FailingClient`. The server itself only owns the trait object and listener task. Lock state is in-memory and lives until the spawned task is aborted or the backing manager drops.

Dependencies and integration points: generated `rustfs_protos::proto_gen::node_service`, `rustfs_lock`, serde JSON, flatbuffers ping model, tonic server, Tokio TCP listener, and `tokio_stream`.

Risks: the implementation must satisfy the full generated `NodeService` trait, so protocol additions may break compilation until new methods are stubbed. Returning application errors inside OK gRPC responses mirrors existing node-service behavior but can obscure transport failures. Batch methods depend on returned result ordering from the backing client. The server has no graceful shutdown handle beyond aborting the task.

Test signals: enables local multi-node gRPC lock tests without full RustFS nodes. The unimplemented methods also ensure accidental non-lock RPC use fails clearly.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/reliant/grpc_lock_server.rs -->
