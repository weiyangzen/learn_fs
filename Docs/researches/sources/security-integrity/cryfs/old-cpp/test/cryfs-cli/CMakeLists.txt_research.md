# sources/security-integrity/cryfs/old-cpp/test/cryfs-cli/CMakeLists.txt

Purpose: Defines the `cryfs-cli-test` target and its test source manifest. It wires CLI behavior tests, program-options tests, version checking, integrity checks, and unmount tests into CTest.

Important APIs and types: CMake lists sources, creates the executable, links `my-gtest-main`, `googletest`, `cryfs-cli`, `cryfs-unmount`, and `fspp-fuse`, registers `add_test`, enables style warnings, and activates C++14.

Control flow: During build, all listed CLI test sources are compiled into one runner. CTest runs the executable as `cryfs-cli-test`.

State and persistence behavior: Build-system state only. Runtime persistence is owned by individual tests that create temp basedirs/mountpoints.

Dependencies and integration points: Integrates CLI library, unmount CLI, and FUSE test support.

Risks: Missing a source removes coverage silently. Linking FUSE-related libraries can make the test target platform-sensitive.

Test signals: Successful build/link and CTest registration of the CLI test runner.
