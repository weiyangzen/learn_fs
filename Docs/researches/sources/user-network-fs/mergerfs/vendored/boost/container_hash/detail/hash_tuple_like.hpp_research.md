# sources/user-network-fs/mergerfs/vendored/boost/container_hash/detail/hash_tuple_like.hpp

Purpose: Adds hashing support for tuple-like types that expose `std::tuple_size` and `get<I>` but are not also detected as ranges.

Important APIs, types, and functions: `hash_combine_tuple_like<I,T>` recursively visits tuple elements, `hash_tuple_like(T const&)` builds a seed from element hashes, and the constrained `boost::hash_value(T const&)` overload enables tuple-like hashing through `container_hash::is_tuple_like`.

Control flow: Compile-time recursion stops when `I == tuple_size<T>::value`; otherwise it imports `std::get`, combines element `I`, and recurses to `I + 1`.

State and persistence behavior: No persistent state; the seed is local to one hash call.

Dependencies and integration points: Depends on `hash_fwd.hpp`, `is_tuple_like.hpp`, `is_range.hpp`, `<type_traits>`, and `<utility>`. Included by `hash.hpp` so `boost::hash` can use ADL-friendly tuple element access.

Risks: Ambiguity is avoided by excluding range types, but custom types that satisfy both tuple-like and range contracts rely on that ordering. Invalid `tuple_size`/`get` definitions fail at compile time.

Test signals: Compile and hash `std::tuple`, `std::pair`-like custom tuple types, `std::array` as a range rather than tuple path, and empty tuple-like types.
