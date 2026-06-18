# sources/user-network-fs/mergerfs/vendored/boost/container_hash/is_tuple_like.hpp

Purpose: Detects tuple-like types for tuple element hashing.

Important APIs, types, and functions: Public `boost::container_hash::is_tuple_like<T>` driven by whether `std::tuple_size<T>::value` is well-formed.

Control flow: Compile-time SFINAE only.

State and persistence behavior: No state.

Dependencies and integration points: Used by `hash_tuple_like.hpp` and indirectly by `hash.hpp`. Depends on `<tuple>` and `<type_traits>`.

Risks: Detects tuple-size availability, not all `get<I>` validity; a type can pass this trait and still fail when hashed.

Test signals: Static assertions for `std::tuple`, `std::pair`, `std::array`, custom tuple-like types, and classes without tuple metadata.
