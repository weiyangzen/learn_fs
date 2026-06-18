# sources/security-integrity/cryfs/old-cpp/test/cryfs-cli/program_options/testutils/ProgramOptionsTestBase.h

Purpose: This header provides `ProgramOptionsTestBase`, a small Google Test base fixture for command-line program-option tests. Its main job is a reusable vector comparison helper for argument-list assertions.

Important APIs/types/functions: It includes `gtest/gtest.h`, derives `ProgramOptionsTestBase` from `::testing::Test`, and exposes `EXPECT_VECTOR_EQ`, which checks vector sizes and then compares each indexed element.

Control flow: Tests subclass the fixture, build expected and actual vectors, and call `EXPECT_VECTOR_EQ`; the helper first verifies cardinality, then loops through the expected vector to produce per-position equality failures.

State and persistence behavior: There is no persistent state. The only state is local vector data supplied by each test case.

Dependencies and integration points: The helper is consumed by `UtilsTest.cpp` and any other CLI option parser tests that need stable assertions on `std::vector<std::string>` results.

Risks: If vector sizes differ, the loop still uses the expected vector's size, so callers depend on Google Test failure reporting rather than early return. The helper is intentionally narrow and does not provide diff-style diagnostics.

Test signals: Fixture users get direct size equality and element-by-element equality checks for parsed argument vectors.
