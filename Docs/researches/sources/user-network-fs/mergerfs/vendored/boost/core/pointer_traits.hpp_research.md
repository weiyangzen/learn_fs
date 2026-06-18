# sources/user-network-fs/mergerfs/vendored/boost/core/pointer_traits.hpp

Purpose: Portable implementation of pointer traits for raw and fancy pointer types.

Important APIs, types, and functions: `boost::pointer_traits<T>`, raw pointer specialization, nested `element_type`, `difference_type`, `rebind_to<U>`, and static `pointer_to`. Also exposes `to_address` overloads for raw and fancy pointers when supported.

Control flow: SFINAE derives element type from `T::element_type` or first template argument, derives difference type from `T::difference_type` or `std::ptrdiff_t`, and chooses `T::rebind<U>` or template rebinding. `pointer_to` calls pointer-specific `pointer_to` or raw `addressof`.

State and persistence behavior: No state.

Dependencies and integration points: Used by allocator access and container internals that support fancy pointers. Depends on `addressof.hpp` and Boost config.

Risks: Template rebinding is heuristic for custom pointer templates. `to_address` recursion depends on pointer-like `operator->`. Void pointer handling is special.

Test signals: Static assertions for raw pointers, smart/fancy pointer mocks, rebind behavior, pointer_to address identity, and `to_address` through nested pointer wrappers.
