# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/pointer/cast_include_test.cpp

Purpose: Compile-only include test for `cpp-utils/pointer/cast.h`.

Important APIs and types: Includes the pointer cast helper header.

Control flow: No runtime tests in this file.

State and persistence behavior: No state or persistence.

Dependencies and integration points: Guards public pointer casting helpers used in ownership/conversion code.

Risks: Does not validate cast safety or runtime checks; `cast_test.cpp` covers behavior.

Test signals: Successful direct header inclusion.
