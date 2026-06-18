# sources/security-integrity/cryfs/old-cpp/test/CMakeLists.txt

Purpose: top-level CMake test tree entry point.

Important APIs/types/functions: `BUILD_TESTING`, `include_directories(../src)`, and `add_subdirectory` calls for test support and component test suites.

Control flow: only active when `BUILD_TESTING` is true. Adds gtest main, gitversion, cpp-utils, fspp except on MSVC, parallelaccessstore, blockstore, blobstore, cryfs, and cryfs-cli tests.

State and persistence behavior: no runtime state; configures which tests are built.

Dependencies and integration points: integrates all old C++ test subdirectories with source includes.

Risks and test signals: fspp tests are disabled on MSVC due a TODO, leaving Windows-specific fspp/Dokan behavior less covered.
