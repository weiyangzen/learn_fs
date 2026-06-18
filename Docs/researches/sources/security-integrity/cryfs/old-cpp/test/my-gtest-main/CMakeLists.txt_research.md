# sources/security-integrity/cryfs/old-cpp/test/my-gtest-main/CMakeLists.txt

Purpose: builds the shared static library that supplies a common Google Test/Mock main function.

Important APIs/targets: creates `my-gtest-main` from `my-gtest-main.cpp`, links `googletest` and `cpp-utils`, adds Boost filesystem/system, exposes the current directory as a public include path, and enables C++14/style warnings.

Control flow/state: build-only file.

Dependencies/integration: used by multiple CryFS test executables that need one consistent `main()` and access to `get_executable()`.

Risks: because the library is static and public-includes `.`, duplicate symbols would occur if a test also defines `main()`.

Test signals: all linked test targets depend on this target building successfully.
