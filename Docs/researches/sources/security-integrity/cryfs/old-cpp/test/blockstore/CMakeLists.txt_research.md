# sources/security-integrity/cryfs/old-cpp/test/blockstore/CMakeLists.txt

Purpose: CMake definition for the `blockstore-test` executable.

Important APIs/types/functions: target `blockstore-test`, sources `BlockStoreUtilsTest.cpp` and `ParallelAccessBlockStoreTest_Specific.cpp`, link libraries `my-gtest-main`, `googletest`, and `blockstore`, plus `add_test`.

Control flow: builds and registers the blockstore test executable when parent testing is enabled.

State and persistence behavior: no runtime state; test behavior is in listed source files and subdirectories.

Dependencies and integration points: connects blockstore tests to the project CTest harness and build warning/C++14 helpers.

Risks and test signals: the cache test files in this subset are not listed directly here, implying they may be included by another nested CMake file or omitted from this old test target.
