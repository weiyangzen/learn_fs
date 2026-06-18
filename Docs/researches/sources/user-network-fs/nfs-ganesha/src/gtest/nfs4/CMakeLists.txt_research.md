# sources/user-network-fs/nfs-ganesha/src/gtest/nfs4/CMakeLists.txt

## Purpose
This CMake file builds four NFSv4 latency test executables: lookup, putfh, rename, and link. Each executable is compiled from its matching `.cc` file and linked against the Ganesha server and test/runtime libraries.

## Important APIs, Types, And Functions
Targets are `test_nfs4_lookup_latency`, `test_nfs4_putfh_latency`, `test_nfs4_rename_latency`, and `test_nfs4_link_latency`. Each target uses `add_executable`, `add_sanitizers`, `target_link_libraries`, and `set_target_properties(... COMPILE_FLAGS "${UNITTEST_CXX_FLAGS}")`.

## Control Flow, State, And Persistence
The file is declarative build configuration. For each test it sets a `_SRCS` variable with one source file, defines the executable, adds sanitizer instrumentation, links required libraries, and applies unit-test C++ flags. It creates no runtime state itself.

## Dependencies And Integration Points
All targets link `ganesha_nfsd`, `${LIBTIRPC_LIBRARIES}`, `${UNITTEST_LIBS}`, `${LTTNG_LIBRARIES}`, `${LTTNG_CTL_LIBRARIES}`, and `${GPERFTOOLS_LIBRARIES}`. This aligns the NFSv4 latency tests with direct Ganesha server symbols, RPC/XDR support, GoogleTest, LTTng event control, and optional profiling.

## Risks And Test Signals
The file repeats nearly identical target definitions, which is simple but easy to drift if a new common dependency is added. Since each executable links `ganesha_nfsd`, build failures here often signal missing server symbols or library configuration rather than test logic issues. Sanitizer attachment is a useful build-time signal for memory and undefined-behavior checks.
