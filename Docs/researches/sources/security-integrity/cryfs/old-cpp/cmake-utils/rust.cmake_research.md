# sources/security-integrity/cryfs/old-cpp/cmake-utils/rust.cmake

Purpose: Adds a Rust static-library companion to a C++ CMake target, including generated `cxx::bridge` C++ files and link wiring for cross-language calls.

Important APIs and types: The public function is `target_add_rust_companion(TARGET_NAME ...)` with arguments `RUST_LIB_NAME`, `RUST_CRATE_NAME`, `RUST_TARGET_NAME`, `TARGET_NAME`, `RUST_DIR`, and `RUST_BRIDGES`.

Control flow: The function selects `cargo build` or `cargo build --release` based on `CMAKE_BUILD_TYPE`, computes generated bridge `.cc` paths under the binary dir, creates a static bridge-file library and interface companion target, sets include directories, optionally enables clang/lld linker-plugin LTO when the C++ target has IPO and compiler support, globs Rust sources excluding `/target/`, adds a custom command that runs Cargo with `CARGO_TARGET_DIR` and `RUSTFLAGS`, links pthread/dl and the Rust staticlib inside a linker start/end group, links the companion into the target, and registers `cargo test`.

State and persistence behavior: Cargo artifacts and generated cxxbridge files are written under the CMake binary directory's Rust subdirectory. The source tree is not modified.

Dependencies and integration points: Used by `src/blockstore/CMakeLists.txt` for the Rust blockstore bridge. It depends on Cargo, Rust cxx bridge generation, CMake custom commands, clang/lld for optional LTO, and Unix linker flags.

Risks: The function is Unix/linker specific (`pthread`, `dl`, `-Wl,--start-group`) and likely not portable without guards. Release handling only distinguishes Debug from everything else. Source globbing is coarse and can miss dependency changes outside the Rust dir or over-trigger builds. Optional LTO depends on LLVM compatibility between Rust and Clang.

Test signals: Successful CMake target build plus the added `cargo test` CTest entry demonstrate integration. Blockstore bridge compilation is the main consumer signal.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/cmake-utils/rust.cmake` completely for this pass (85 lines, 5293 bytes).
