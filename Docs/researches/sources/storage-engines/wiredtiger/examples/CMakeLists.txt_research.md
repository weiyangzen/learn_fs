# sources/storage-engines/wiredtiger/examples/CMakeLists.txt

Purpose: wires the example subtree into the build and preserves legacy executable layout expected by some examples.

Important APIs and control flow: `add_subdirectory(c)` delegates C example target creation. `add_custom_command(OUTPUT wt ...)` copies `$<TARGET_FILE:wt>` into `${CMAKE_CURRENT_BINARY_DIR}/wt`, and `add_custom_target(sym_wt_examples ALL ...)` makes the copy part of the default build.

State and persistence: writes a copied `wt` binary in the examples binary directory. No source state is modified.

Dependencies and integration: depends on the `wt` target and CMake generator expressions. This is specifically integrated with examples, such as backup/log examples, that run `../../wt` relative to their own binary directory to match the historical autoconf layout.

Risks: if the target file path or relative runtime layout changes, examples using hard-coded `../../wt` can fail even when compilation succeeds. The custom command output name `wt` can collide with generated files in the same binary directory if layout changes.

Test signals: building the `sym_wt_examples` target and running examples that invoke `../../wt` verifies both the copy and relative path compatibility.
