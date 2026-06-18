## sources/storage-engines/foundationdb/bindings/c/test/workloads/RustWorkload/src/lib.rs

Purpose: Rust workload framework layer that maps Rust traits to the C workload ABI. It defines how concrete Rust workloads are boxed, exposed through an `FDBWorkload` vtable, and created by an exported factory symbol.

Important APIs and types: `MockDatabase` is a non-null `FDBDatabase` pointer placeholder. `RustWorkload` declares lifecycle methods `setup`, `start`, `check`, `get_metrics`, and `get_check_timeout`, plus an associated static vtable. `RustWorkloadFactory` defines `create`. `register_factory!` emits the `workloadCFactory` symbol expected by the loader.

Control flow: `RustWorkload::wrap` boxes `self`, stores the raw pointer as `OpaqueWorkload`, and assigns the static vtable. Each unsafe extern callback casts the opaque pointer back to `W`, wraps raw database/promise/metrics arguments, and calls the Rust trait method. `workload_drop` reconstructs and drops the boxed workload.

State and persistence: workload state lives in a Rust `Box` controlled by the C ABI free callback. No database persistence is implemented here.

Dependencies and integration points: uses the wrappers from `bindings.rs` and is extended by `mock.rs`. It is the Rust analog of `CWorkload.c` and must match `CWorkload.h` layout exactly.

Risks: all FFI callbacks are unsafe and assume valid non-null pointers from the loader. Double-free or use-after-free can occur if `free` is called while callbacks still reference the workload. The macro must be invoked once to avoid duplicate symbol definitions.

Test signals: validates that Rust trait implementations can be loaded as C ABI workloads.
