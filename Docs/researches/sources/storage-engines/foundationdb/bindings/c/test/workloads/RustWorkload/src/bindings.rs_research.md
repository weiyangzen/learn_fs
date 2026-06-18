## sources/storage-engines/foundationdb/bindings/c/test/workloads/RustWorkload/src/bindings.rs

Purpose: safe-ish Rust convenience layer over bindgen-generated C workload ABI definitions. It converts raw generated types into Rust wrapper types for workload context, promises, metrics, string conversion, and severity values.

Important APIs and types: re-exports `FDBDatabase`, `FDBMetrics`, `FDBPromise`, `FDBWorkload`, `FDBWorkloadContext`, `FDBWorkload_VT`, and `OpaqueWorkload`. Defines `WorkloadContext`, `Promise`, `Metrics`, `Metric`, and `Severity`. `str_from_c` and `str_for_c` handle C string conversion. The `with!` macro calls vtable functions from generated C structs.

Control flow: wrapper methods convert Rust arguments to temporary `CString`s, build raw structs like `FDBStringPair` or `FDBMetric`, invoke C vtable calls, then rely on synchronous consumption by the C++ side. `Promise::send` consumes the promise wrapper; `Drop` calls the promise free vtable. `Metrics::extend` reserves then pushes each metric.

State and persistence: wraps borrowed simulation context and promise/metrics sinks. Option retrieval intentionally frees the returned `FDBString` and treats an empty default as `None`.

Dependencies and integration points: includes generated bindings from `OUT_DIR`, and is consumed by `lib.rs` and `mock.rs` to implement an exported Rust workload factory.

Risks: `unwrap_unchecked` assumes all vtable function pointers are present. Temporary C string lifetimes are only safe if the C++ callee copies synchronously. `Promise` drop always frees, so ownership must not be duplicated after `send`.

Test signals: exercises Rust bindings for trace, options, client metadata, randomness, promise completion, and metrics through the mock workload.
