## sources/storage-engines/foundationdb/bindings/c/test/workloads/RustWorkload/test_file.toml

Purpose: FoundationDB simulation test configuration for loading and running the Rust external workload.

Important settings: defines a single `[[test]]` named `Rust_CAPI_Test` with one `External` workload. `useCAPI = true` selects the C workload ABI, `libraryPath = './target/release'`, `libraryName = 'rust_workload'`, and `workloadName = 'MockWorkload'` target the Rust cdylib and factory implementation. `my_rust_option = 'my_value'` feeds option retrieval in `MockFactory`.

Control flow: the simulator reads this TOML, loads the dynamic library from the release target directory, invokes `workloadCFactory`, and then drives setup/start/check/metrics through the returned vtable.

State and persistence: no direct database state; it configures runtime dynamic loading and workload options.

Dependencies and integration points: coupled to Cargo output naming, the `MockWorkload` string in `mock.rs`, and the external workload loader.

Risks: path/name mismatches are likely if Cargo target names or platform library prefixes/suffixes differ. Release build must exist before running this test file.

Test signals: verifies end-to-end loading of the Rust workload bridge when paired with a built cdylib.
