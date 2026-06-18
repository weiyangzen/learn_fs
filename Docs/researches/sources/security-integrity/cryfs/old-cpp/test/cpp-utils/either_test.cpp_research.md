# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/either_test.cpp

Purpose: Exhaustive behavioral test suite for `cpputils::either<L,R>`, including construction, factories, copy/move semantics, accessors, optional access, same-type variants, movable-only values, multi-argument construction, equality, streaming, destructor behavior, and storage size.

Important APIs and types: Uses `either`, `make_left`, `make_right`, `left/right`, `left_opt/right_opt`, `is_left/is_right`, emplace-style construction, comparison operators, stream output, `MovableOnly`, destructor callback helper classes, Boost optional, and GoogleMock.

Control flow: Matrix helper functions run the same expectations over multiple construction paths. Later tests exercise copy/move construction and assignment for left/right alternatives, mutation through accessors, equality comparisons, and destructor counts after copies/moves/assignments.

State and persistence behavior: Variant state is purely in-memory with one active alternative. Destructor tests use counters/callbacks to prove active object lifetime transitions.

Dependencies and integration points: Protects a core utility similar to `std::variant`/`Either`, used by code that needs explicit success/error or left/right results.

Risks: The suite locks in moved-from behavior and compact storage expectations. Exception-safety and noexcept tag coverage is noted as a TODO.

Test signals: Correct active side, expected access exceptions, optional values, moved/copy-preserved payloads, destructor calls, comparisons, output text, and no excess storage overhead.
