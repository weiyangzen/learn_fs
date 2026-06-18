# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/pointer/optional_ownership_ptr_test.cpp

Purpose: Tests `optional_ownership_ptr`, a pointer wrapper that can either own or non-own a pointee while presenting pointer-like access.

Important APIs and types: Uses the optional ownership pointer header, GoogleTest, and local test objects/destructor counters.

Control flow: Tests create owning and non-owning instances, dereference/access pointees, move or reset wrappers, and verify destruction behavior matches ownership mode.

State and persistence behavior: In-memory pointer ownership and object lifetime. Destructor counters or flags provide test state.

Dependencies and integration points: Useful where APIs optionally assume responsibility for object deletion without changing call syntax.

Risks: The key risk is double-free or leak when ownership mode changes or wrappers move. Non-owning pointers also risk dangling references outside the test's controlled lifetime.

Test signals: Correct dereference values, expected destructor calls for owning pointers, no destructor call for non-owning pointers, and valid move behavior.
