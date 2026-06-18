# sources/storage-engines/tikv/components/service/src/service_manager.rs

Purpose: a cloneable handle for requesting gRPC service pause/resume and exposing current serving state.

Important APIs and types: private `GrpcServiceStatus` has `Init`, `Serving`, and `NotServing`. `GrpcServiceManager` stores `Arc<Atomic<GrpcServiceStatus>>` plus a TiKV mpsc sender. Public constructors are `new` and `dummy`; public actions are `pause`, `resume`, and `is_paused`.

Control flow: `pause` is idempotent if already paused; otherwise it sends `ServiceEvent::PauseGrpc` and stores `NotServing` only if send succeeds. `resume` mirrors this with `ResumeGrpc` and `Serving`. `is_serving` is private and used to avoid duplicate resume sends.

State and persistence behavior: state is in-memory relaxed atomic status. It deliberately tracks requested service state, not necessarily full server-side completion. No persistence.

Dependencies and integration points: used by `server2.rs` to give status service and raftstore/node code a way to pause or resume the gRPC server through the main event loop.

Risks: status updates occur after successful send, before the receiver acts, so callers must not treat the flag as a synchronous server-state guarantee. `dummy` starts in `Init`, so tests using it must account for resume semantics from a non-serving/non-paused initial state.

Test signals: no direct tests in this file.
