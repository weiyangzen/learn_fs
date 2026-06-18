## sources/storage-engines/foundationdb/bindings/c/test/workloads/RustWorkload/build.rs

Purpose: Cargo build script that generates Rust FFI bindings for the FoundationDB workload ABI header.

Important APIs and functions: `bindgen::Builder::default().header(c_workload_h).generate()` reads `../../../foundationdb/CWorkload.h`; `println!("cargo:rerun-if-changed=...")` ties rebuilds to header changes; `write_to_file(out_path.join("bindings.rs"))` stores generated bindings in Cargo `OUT_DIR`.

Control flow: resolve a relative header path, tell Cargo when to rerun, generate bindings, resolve `OUT_DIR`, and write `bindings.rs`. Failures panic with clear `expect` messages.

State and persistence: persists only generated Rust binding code in Cargo's build output directory. It does not modify repository files.

Dependencies and integration points: depends on `bindgen`, clang/libclang availability, and the header path being valid relative to the crate root. `src/bindings.rs` includes the generated output at compile time.

Risks: relative path drift or header dependency changes not tracked by the single rerun directive can lead to stale or failed generated bindings. Generated layout must match the C/C++ workload loader ABI.

Test signals: build success validates header parseability and Rust wrapper compatibility with current ABI definitions.
