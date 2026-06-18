# sources/security-integrity/cryfs/old-cpp/src/blockstore/CMakeLists.txt

Purpose: Defines the legacy `blockstore` static library target and wires it to C++ utilities, Boost, style rules, C++ standard settings, and a Rust companion library.

Important APIs and types: `SOURCES` lists blockstore utilities, test fake, parallel access, caching cache, mock, and rustbridge implementation files. It calls `add_library(blockstore STATIC ...)`, `target_link_libraries(blockstore PUBLIC cpp-utils)`, `target_add_boost`, `target_enable_style_warnings`, `target_activate_cpp14`, includes `rust`, and calls `target_add_rust_companion`.

Control flow: Configure creates the static target from C++ sources, applies common build helper functions, then registers Rust bridge files for `cryfs-cppbridge` with bridges `src/blockstore.rs`, `src/blobstore.rs`, and `src/fsblobstore.rs`.

State and persistence behavior: Build outputs include the C++ static library, generated Rust bridge C++ files, and Cargo artifacts under the build tree.

Dependencies and integration points: This target sits between lower-level `cpp-utils`/`parallelaccessstore` and higher-level blobstore/cryfs code. It includes both legacy C++ blockstore adapters and Rust bridge integration.

Risks: The source list contains several `.cpp` files that only include template headers, so removing them may affect IDE/build source visibility but not logic. Rust companion setup is platform-sensitive. Test fake/mock implementations are compiled into the main static library, not isolated test-only code.

Test signals: `blockstore-test`, rust companion cargo tests, and any higher-level blobstore/cryfs tests validate this target.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/src/blockstore/CMakeLists.txt` completely for this pass (39 lines, 1270 bytes).
