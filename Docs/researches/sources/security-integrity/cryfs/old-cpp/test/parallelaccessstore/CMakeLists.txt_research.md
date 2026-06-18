# sources/security-integrity/cryfs/old-cpp/test/parallelaccessstore/CMakeLists.txt

Purpose: builds and registers the `parallelaccessstore-test` executable.

Important APIs/targets: uses `ParallelAccessBaseStoreTest.cpp` and `DummyTest.cpp`, links `my-gtest-main`, `googletest`, and `parallelaccessstore`, registers with CTest, and applies style/C++14 helpers.

Control flow/state: build graph only.

Dependencies/integration: ensures the `parallelaccessstore` library can be included/linked in the test suite.

Risks: current source tests are skeletal, so the target mainly catches build/interface failures rather than behavior regressions.

Test signals: `DummyTest` guarantees at least one gtest case; include-only test catches header compile errors.
