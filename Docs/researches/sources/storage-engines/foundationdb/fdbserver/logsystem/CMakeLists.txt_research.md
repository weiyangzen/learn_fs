# sources/storage-engines/foundationdb/fdbserver/logsystem/CMakeLists.txt

Purpose: Defines the FoundationDB `fdbserver_logsystem` static library target and its link/unit-test wiring inside the fdbserver build.

Important APIs/types/functions: Uses project CMake helpers `fdb_find_sources`, `add_flow_target`, `add_fdbserver_link_test`, `add_fdbserver_unit_test`, and `configure_fdbserver_common_includes`. It then sets public and private include directories with `target_include_directories` and links `fdbserver_core` plus `fdbserver_kvstore` through `target_link_libraries`.

Control flow: CMake first discovers all sources in the directory into `FDBSERVER_LOGSYSTEM_SRCS`, builds them into a static `fdbserver_logsystem` Flow target, adds a link test against the logsystem/core/kvstore stack, adds a unit-test target named `fdbserver_logsystem_test` in the `logsystem` suite, configures common fdbserver includes, exposes the local `include` directory publicly, and links the static library's public dependencies.

State and persistence behavior: No runtime persistence is implemented here. The build file controls generated build graph state: which source files are compiled into the logsystem library, which include paths are exported to dependents, and which validation targets exist.

Dependencies and integration points: Integrates the logsystem module with the broader Flow/CMake build infrastructure and with fdbserver's core and kvstore libraries. The public include directory is the interface consumed by other fdbserver components such as master/recovery, commit proxy, TLog, and disk-queue adapter callers.

Risks: `fdb_find_sources` means new files in this directory can be picked up automatically, so accidental files may enter the static library. Link and unit tests are only as complete as the sources and test registration behind the helper macros. Publicly linking `fdbserver_core` and `fdbserver_kvstore` exposes those dependency assumptions to downstream targets.

Test signals: Build success of `fdbserver_logsystem`, `fdbserver_logsystemlinktest`, and `fdbserver_logsystem_test` is the direct signal. A clean dependency graph should compile after adding/removing logsystem files, and downstream fdbserver targets should see headers under the public `include` directory without extra include plumbing.
