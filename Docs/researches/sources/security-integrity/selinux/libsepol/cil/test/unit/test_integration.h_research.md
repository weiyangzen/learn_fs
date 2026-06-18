# sources/security-integrity/selinux/libsepol/cil/test/unit/test_integration.h

Purpose: Declares the CIL integration test entry points.

Important APIs and types: Exposes `test_min_policy(CuTest *)` and `test_integration(CuTest *)`.

Control flow: No logic exists in the header; it is a suite registration contract for `test_integration.c`.

State and persistence: No state is declared. The implementations create policy files by running external compilers.

Dependencies and integration points: Depends on `CuTest.h` and the CIL test runner.

Risks: Prototype drift breaks builds or loses integration coverage.

Test signals: The suite compiles and both commands are run by the test binary.
