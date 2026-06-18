# sources/user-network-fs/mergerfs/vendored/boost/unordered/unordered_flat_map_fwd.hpp

## Purpose

This Boost.Unordered public forward header declares `boost::unordered::unordered_flat_map` and its non-member operations without including the full implementation. It reduces compile-time coupling for code that only needs declarations.

## Important APIs, types, and functions

The main declaration is `template<class Key, class T, class Hash = boost::hash<Key>, class KeyEqual = std::equal_to<Key>, class Allocator = std::allocator<std::pair<const Key, T>>> class unordered_flat_map;`.

It also declares `operator==`, `operator!=`, and non-member `swap`, with `swap` using `noexcept(noexcept(lhs.swap(rhs)))` to mirror the member swap's exception specification. When `<memory_resource>` is available, it defines `boost::unordered::pmr::unordered_flat_map` as an alias using `std::pmr::polymorphic_allocator<std::pair<const Key, T>>`.

Finally, it brings the type into namespace `boost` with `using boost::unordered::unordered_flat_map`.

## Control Flow

There is no runtime control flow. Preprocessor logic includes memory-resource support unless `BOOST_NO_CXX17_HDR_MEMORY_RESOURCE` is defined, and enables `#pragma once` through Boost.Config.

## State and Persistence Behavior

The file declares types and functions only. It creates no objects and owns no state. ABI and persistence concerns are deferred to the full unordered flat map implementation.

## Dependencies and Integration Points

It depends on Boost.Config, `boost/container_hash/hash_fwd.hpp`, `<functional>`, `<memory>`, and optionally `<memory_resource>`. It integrates with users that forward-declare or store pointers/references to `unordered_flat_map`, and with PMR-aware code that wants the standard polymorphic allocator spelling.

## Risks and Edge Cases

Default template arguments in forward declarations must remain synchronized with the full definition. The PMR alias depends on standard library support and is absent when memory-resource headers are disabled. Non-member declarations must match implementation signatures exactly to avoid ODR or overload issues.

## Test Signals

Compile tests should include this header alone, declare pointers/references, use the `boost::unordered_flat_map` using-declaration, and compile PMR aliases when the standard library supports them. Link tests should verify equality and swap declarations resolve when the full implementation is included elsewhere.
