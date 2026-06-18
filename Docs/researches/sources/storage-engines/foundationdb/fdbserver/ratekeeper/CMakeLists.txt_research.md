# sources/storage-engines/foundationdb/fdbserver/ratekeeper/CMakeLists.txt

Purpose: defines the `fdbserver_ratekeeper` static library target and its build/test integration.

Important APIs and functions: `fdb_find_sources(FDBSERVER_RATEKEEPER_SRCS)` gathers local sources. `add_flow_target(STATIC_LIBRARY NAME fdbserver_ratekeeper ...)` builds the library. `add_fdbserver_link_test` and `add_fdbserver_unit_test` wire link and unit-test validation against `fdbserver_core`. `configure_fdbserver_common_includes`, `target_include_directories`, and `target_link_libraries` publish the `include` tree and add private local includes.

Control flow, state, and persistence: this is declarative CMake with no runtime state. Its main effect is target graph construction, include visibility, and test target registration.

Dependencies and integration: integrates ratekeeper code with the larger fdbserver build. Public headers under `ratekeeper/include` become visible to consumers, while implementation headers in the directory stay private.

Risks and test signals: risks are missing new sources if the source discovery macro changes, missing public include paths, and link-test gaps after dependencies are added. Build signals are successful `fdbserver_ratekeeper`, `fdbserver_ratekeeperlinktest`, and `fdbserver_ratekeeper_test` targets.
