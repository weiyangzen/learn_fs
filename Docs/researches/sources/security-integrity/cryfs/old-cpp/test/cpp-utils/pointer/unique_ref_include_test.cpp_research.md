# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/pointer/unique_ref_include_test.cpp

Purpose: Compile-only include test for `cpp-utils/pointer/unique_ref.h`.

Important APIs and types: Includes the public non-null unique ownership wrapper header.

Control flow: No runtime tests.

State and persistence behavior: No state or persistence.

Dependencies and integration points: Protects a widely used ownership abstraction across CryFS code.

Risks: Does not test ownership behavior; `unique_ref_test.cpp` provides broad semantic coverage.

Test signals: Successful direct header compilation.
