# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/pointer/cast_test.cpp

Purpose: Tests pointer casting helpers for raw pointers and smart/ownership wrappers, including valid up/down casts and invalid cast handling.

Important APIs and types: Uses `cpp-utils/pointer/cast.h`, GoogleTest, and local base/derived test classes.

Control flow: Test cases construct objects through different pointer forms, call cast helpers, and assert resulting object identity/value or failure behavior.

State and persistence behavior: In-memory object ownership and pointer identity only. No persistent state.

Dependencies and integration points: These helpers support safe conversions in code using `unique_ref`, `unique_ptr`, and related pointer abstractions.

Risks: Cast behavior may differ with RTTI settings or polymorphic base requirements. Ownership-preserving casts must avoid leaks and double deletes.

Test signals: Correct pointer identity after valid casts, expected failure on invalid casts, and ownership transfer without leaks.
