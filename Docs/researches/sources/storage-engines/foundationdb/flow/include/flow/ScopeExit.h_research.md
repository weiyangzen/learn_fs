<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/ScopeExit.h -->
# sources/storage-engines/foundationdb/flow/include/flow/ScopeExit.h

Purpose: This header defines a minimal RAII guard that executes a provided callable when the guard leaves scope.

Important APIs and types: `template <typename Func> class ScopeExit` stores `std::decay_t<Func> fn`, constructs from a forwarding reference, and calls `fn()` in its destructor.

Control flow: Construction captures the callable. Destruction unconditionally invokes it. There is no cancellation, release, move handling, or exception guard in this minimal implementation.

State and persistence behavior: The only state is the stored callable. There is no persistence.

Dependencies and integration points: The header relies on standard type utilities through included context and can be used anywhere a small cleanup action is needed in Flow code.

Risks: If the callable throws during stack unwinding, normal C++ termination rules apply. Because no move/copy operations are explicitly deleted, copying behavior depends on the callable and could lead to multiple invocations if a guard is copied. There is no dismiss API.

Test signals: Tests should validate destructor execution on normal and exceptional scope exit, capture-by-reference behavior, and avoid accidental copies in call sites.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/ScopeExit.h -->
