# sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindGTest.cmake

Purpose: Finds GoogleTest libraries and headers for C++ test targets.

Important APIs/types/functions: Consumes `GTEST_PREFIX`; finds `gtest` and `gtest_main` into `GTEST`/`GTEST_MAIN`, finds `gtest/gtest.h`, sets `GTEST_LIBRARIES`, and uses standard package handling.

Control flow: Search variables are resolved, then package success requires `GTEST_LIBRARIES` and `GTEST_INCLUDE_DIR`.

State and persistence behavior: CMake cache variables only.

Dependencies and integration points: Test targets link `${GTEST_LIBRARIES}` and include `${GTEST_INCLUDE_DIR}`.

Risks: Some modern GTest installs provide CMake package targets instead of raw libraries, and library names may be debug-suffixed. The module requires both gtest and gtest_main even if a target supplies its own main.

Test signals: Configure with distro GTest, source-built prefix, missing `gtest_main`, and target linking.
