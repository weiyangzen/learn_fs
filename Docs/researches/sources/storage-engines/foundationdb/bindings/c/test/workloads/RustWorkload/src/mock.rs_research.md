## sources/storage-engines/foundationdb/bindings/c/test/workloads/RustWorkload/src/mock.rs

Purpose: concrete Rust mock workload used to test the Rust workload ABI bridge. It mirrors the C workload sample with lifecycle logging, tracing, metrics, option consumption, and factory selection by workload name.

Important APIs and types: `MockWorkload` stores `name`, `client_id`, and `WorkloadContext`. It implements `RustWorkload`. `MockFactory` implements `RustWorkloadFactory`, reads `client_id`, `client_count`, `FDB_WORKLOAD_API_VERSION`, server workload API version, and option `my_rust_option`.

Control flow: factory creation logs metadata, reads the same option twice, and constructs a `MockWorkload` only for `MockWorkload`, panicking on unknown names. `setup`, `start`, and `check` trace a `Test` event with `Layer=Rust` and phase-specific stage, then resolve the promise. `get_metrics` pushes `test=42`; `get_check_timeout` returns 3000; `Drop` logs free.

State and persistence: no database writes. Runtime state is held in the boxed workload created by `wrap` in `lib.rs`.

Dependencies and integration points: registered by `register_factory!(MockFactory)` as `workloadCFactory`; selected by `test_file.toml` via `workloadName = 'MockWorkload'`.

Risks: panic on unknown workload name crosses the dynamic library boundary and may abort the test process. Printed option label says `my_c_option` while reading `my_rust_option`, which is harmless but confusing.

Test signals: confirms Rust lifecycle, trace, metric, timeout, factory, drop, and option retrieval paths.
