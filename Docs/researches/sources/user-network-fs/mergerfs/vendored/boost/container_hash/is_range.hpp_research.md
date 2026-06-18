# sources/user-network-fs/mergerfs/vendored/boost/container_hash/is_range.hpp

Purpose: Detects types with `begin()` and `end()` members for generic range hashing.

Important APIs, types, and functions: Public `boost::container_hash::is_range<T>` and internal SFINAE helper `is_range_` over `std::declval<T const&>().begin()`/`.end()`.

Control flow: Compile-time detection only; true types select the range `hash_value` overloads.

State and persistence behavior: No state.

Dependencies and integration points: Used by `hash.hpp`, `hash_tuple_like.hpp`, and `is_contiguous_range.hpp`. Depends on `<type_traits>` and `<utility>`.

Risks: Only member `begin/end` are recognized; free-function range customization is not. Types with incidental `begin/end` may become hashable by range semantics.

Test signals: Static assertions for STL containers, const containers, custom member ranges, non-ranges, and free-only ranges.
