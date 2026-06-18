# sources/user-network-fs/mergerfs/vendored/boost/unordered/concurrent_flat_map.hpp

Purpose: Provides the public `boost::unordered::concurrent_flat_map` container, a thread-safe open-addressing hash map without iterators, built around visitation and composite operations.

Important APIs, types, and functions: Exposes constructors, assignment, `size`, `empty`, `visit`, `cvisit`, bulk visit, `visit_all`, `visit_while`, `insert`, `insert_or_assign`, `insert_or_visit`, `insert_and_visit`, `emplace`, `try_emplace`, `erase`, `erase_if`, `merge`, `count`, `contains`, `rehash`, `reserve`, `get_allocator`, `hash_function`, `key_eq`, optional stats, `operator==`, `swap`, free `erase_if`, serialization, deduction guides, and a `pmr` alias from the forward header.

Control flow: The class is mostly a thin API adapter over `detail::foa::concurrent_table<flat_map_types<...>>`. Operations validate callback invocability with static-assert macros, then delegate to table methods. Insert-or-assign uses `try_emplace_or_visit` and mutates the mapped value in the visit path. Range insert loops call table emplacement one element at a time. Serialization delegates the table as an NVP.

State and persistence behavior: Persistent container state is entirely `table_`: allocator, hash, predicate, slot arrays, locks, size, and optional stats. No iterators are exposed because concurrent access is mediated through callbacks under table locks.

Dependencies and integration points: Integrates Boost.ContainerHash, allocator access, Boost.Serialization, `unordered_flat_map` move construction, FOA type policy, and concurrent table internals.

Risks: User callbacks execute while element/group access is controlled by the table, so reentrant operations are restricted by the lower-level reentrancy check. The API intentionally differs from standard containers; code expecting iterators cannot be ported mechanically. Parallel algorithms are only available when execution support is detected.

Test signals: Tests should cover concurrent inserts/lookups/erases, callback constness, heterogeneous lookup, range and initializer construction, merge, serialization, deduction guides, stats builds, and reentrancy assertions.
