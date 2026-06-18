# sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/concurrent_static_asserts.hpp

Purpose: Centralizes compile-time validation macros for concurrent unordered container APIs.

Important APIs, types, and functions: Defines macros for invocable callbacks, const-invocable callbacks, sequenced execution policies, last/penultimate variadic argument validation, forward iterators, key-compatible iterators, and bulk-visit iterators. Provides `detail::is_invocable`.

Control flow: Macros expand to `static_assert`s. In C++20, execution policy checks reject both unsequenced and parallel-unsequenced policies; in earlier modes only parallel-unsequenced is checked. MP11 utilities select callback positions in variadic APIs.

State and persistence behavior: Compile-time only.

Dependencies and integration points: Used heavily by `concurrent_flat_map` before delegating to `concurrent_table`. Depends on Boost.MP11 and unordered type traits including transparent-key compatibility.

Risks: These diagnostics are template-heavy and can be noisy, but they catch unsafe callbacks and iterator misuse early. Execution policy checks rely on standard library policy type traits.

Test signals: Negative compile tests should cover non-invocable callbacks, incompatible bulk iterators, and rejected unsequenced policies.
