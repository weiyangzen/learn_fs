# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/pointer/unique_ref_boost_optional_gtest_workaround_include_test.cpp

Purpose: Compile-only include test for the Boost optional/GoogleTest workaround supporting `unique_ref` values.

Important APIs and types: Includes `cpp-utils/pointer/unique_ref_boost_optional_gtest_workaround.h`.

Control flow: No runtime logic.

State and persistence behavior: No state or persistence.

Dependencies and integration points: This workaround is included by tests that compare `boost::optional<unique_ref<...>>` or related optional pointer-like values.

Risks: Only catches include breakage; semantic failures would appear in tests using optional `unique_ref` values.

Test signals: Successful compilation.
