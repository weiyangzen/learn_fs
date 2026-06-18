# sources/storage-engines/foundationdb/fdbserver/clustercontroller/CMakeLists.txt

## Purpose
This CMake file defines the `fdbserver_clustercontroller` static library and its link and unit-test targets.

## Important APIs and Build Rules
`fdb_find_sources(FDBSERVER_CLUSTERCONTROLLER_SRCS)` discovers source files in the clustercontroller directory. `add_flow_target(STATIC_LIBRARY NAME fdbserver_clustercontroller SRCS ${FDBSERVER_CLUSTERCONTROLLER_SRCS})` creates the library. `add_fdbserver_link_test()` creates `fdbserver_clustercontrollerlinktest` against clustercontroller, logsystem, and core. `add_fdbserver_unit_test()` creates the `clustercontroller` unit-test target with the same dependencies.

## Control Flow and Integration
Common includes are configured with `configure_fdbserver_common_includes()`. The public include directory is `clustercontroller/include`; the source directory is private. The target links privately with `fdbserver_core` and `fdbserver_logsystem`, matching cluster-controller code that coordinates workers, recovery, and log-system state.

## State, Risks, and Test Signals
There is no runtime state. As with other directory-level FoundationDB CMake files, automatic source discovery can accidentally include new sources if they are placed in the directory. Link and unit-test targets provide build-time validation that clustercontroller sources and tests link against core and logsystem dependencies.
