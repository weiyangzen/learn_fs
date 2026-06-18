# sources/security-integrity/cryfs/old-cpp/test/gitversion/CMakeLists.txt

Purpose: builds and registers the `gitversion-test` executable.

Important APIs/targets: declares `ParserTest.cpp` and `VersionCompareTest.cpp` as sources, creates an executable, links `my-gtest-main`, `googletest`, and `gitversion`, registers it with CTest via `add_test`, and applies local C++14/style-warning helpers.

Control flow/state: no runtime state; it determines build graph and test discovery.

Dependencies/integration: depends on the local `gitversion` library and shared Google Test main library.

Risks: missing helper macros or target names break configuration. The target relies on `my-gtest-main` to provide `main()`.

Test signals: the CTest entry makes parser and comparator regressions visible in normal test runs.
