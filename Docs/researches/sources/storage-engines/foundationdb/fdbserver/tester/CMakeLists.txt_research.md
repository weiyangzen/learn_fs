# sources/storage-engines/foundationdb/fdbserver/tester/CMakeLists.txt

Purpose: Defines the `fdbserver_tester` static library build target and link test.

Important APIs/types/functions: Uses `fdb_find_sources(FDBSERVER_TESTER_SRCS)`, `add_flow_target(STATIC_LIBRARY NAME fdbserver_tester ...)`, `add_fdbserver_link_test(fdbserver_testerlinktest fdbserver_tester fdbserver_core)`, `configure_fdbserver_common_includes`, `target_include_directories(.../include)`, `target_link_libraries(... fdbclient fdbserver_core toml11::toml11)`, and conditional `add_dependencies(fdbserver_tester toml11Project)`.

Control flow: CMake discovers sources, creates a static library, configures public include paths, links dependencies, and ensures vendored `toml11` builds first when not found as a package.

State and persistence behavior: Build-system state only: target graph, include paths, dependencies. No runtime state.

Dependencies and integration points: Pulls together tester orchestration, workload utilities, parser, maintenance, and consistency checker sources. Links to `fdbclient`, `fdbserver_core`, and TOML parsing.

Risks: `fdb_find_sources` makes source inclusion broad; accidental files in the directory can enter the target. TOML dependency handling must match external project naming. Missing public include configuration would break `fdbserver/tester/...` includes.

Test signals: `fdbserver_testerlinktest` verifies link completeness. Build failures around TOML or core symbols indicate integration drift.
