# sources/security-integrity/cryfs/old-cpp/test/fspp/CMakeLists.txt

Purpose: This CMake file defines the `fspp-test` test executable for the CryFS legacy C++ tree. It enumerates the test sources in this subtree, links the executable to the production libraries and Google Test support, registers it with CTest, and applies the repository's C++14 and style-warning helpers.

Important APIs/types/functions: The important build APIs are `project`, `set(SOURCES)`, `add_executable`, `target_link_libraries`, `add_test`, `target_enable_style_warnings`, and `target_activate_cpp14`. The source list is the integration surface: changing it determines which config, filesystem, local-state, fspp interface, and FUSE adapter tests actually run.

Control flow: Configure-time evaluation collects the listed sources into one executable target, then target creation and link steps bind it to the relevant production library. Test execution is delegated to CTest through the `add_test` registration.

State and persistence behavior: The file persists no runtime state. Its state effect is build-system state: generated target metadata, dependency edges, compiler mode, warning policy, and CTest registration in the build directory.

Dependencies and integration points: It integrates this test subtree with `my-gtest-main`, `googletest`, and the matching production libraries. It is the bridge between individual source files and CI/test runners.

Risks: Missing a source in `SOURCES` silently removes coverage from the executable. A stale link library or C++ standard setting can mask source-level correctness by preventing the tests from building.

Test signals: A successful configure/build produces the `fspp-test` executable, and a successful CTest invocation proves all listed source files compiled and linked into the expected test target.
