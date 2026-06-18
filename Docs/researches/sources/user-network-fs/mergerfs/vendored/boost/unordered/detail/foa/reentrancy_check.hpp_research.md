# sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/foa/reentrancy_check.hpp

Purpose: Provides debug-time protection against unsupported reentrant access to the same concurrent unordered container.

Important APIs, types, and functions: Defines `entry_trace`, `reentrancy_checked<LockGuard>`, and `reentrancy_bichecked<LockGuard>` when enabled; otherwise defines pass-through wrappers with the same interface.

Control flow: When reentrancy checking is enabled, `entry_trace` maintains a thread-local linked list of active container addresses. Construction asserts the address is not already present, and destruction/removal clears it. The checked wrappers acquire the underlying lock guard and clear traces when `unlock()` is called.

State and persistence behavior: Uses thread-local transient state only. No cross-thread persistence.

Dependencies and integration points: Used by `concurrent_table` access guards around operations that must not call back into the same table recursively. Depends on Boost.Assert.

Risks: Disabled when `BOOST_UNORDERED_DISABLE_REENTRANCY_CHECK` is set or assertions are void, so release builds may not catch misuse. It detects same-thread reentrancy, not all logical deadlock scenarios.

Test signals: Debug tests should trigger assertions for callbacks that reenter the same container and should allow operations on distinct containers.
