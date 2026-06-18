# sources/security-integrity/cryfs/old-cpp/test/blobstore/CMakeLists.txt

Purpose: CMake definition for the `blobstore-test` executable.

Important APIs/types/functions: target `blobstore-test`, source list for onblocks utility, blob store, blob size/read/write, big blob, and data tree tests; link to `my-gtest-main`, `googletest`, and `blobstore`; `add_test`.

Control flow: compiles all listed unit tests into one executable and registers it with CTest.

State and persistence behavior: no runtime state in the build file; tests use in-memory/fake stores.

Dependencies and integration points: connects blobstore implementation tests to the project test harness and C++14/style warning helpers.

Risks and test signals: source list is explicit, so new tests are not picked up automatically. It currently includes Rust bridge blobstore fixtures even though directory names still say `onblocks`.
