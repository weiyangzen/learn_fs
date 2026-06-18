# sources/user-network-fs/mergerfs/vendored/boost/container_hash/is_unordered_range.hpp

Purpose: Detects unordered associative containers so hashing can be order-insensitive.

Important APIs, types, and functions: Public `boost::container_hash::is_unordered_range<T>`, implemented by detecting `typename T::hasher`.

Control flow: Compile-time SFINAE only; true types select `hash_unordered_range`.

State and persistence behavior: No state.

Dependencies and integration points: Used by `hash.hpp` to distinguish ordered ranges from unordered containers.

Risks: The `hasher` nested type is a heuristic. Custom ordered containers with a `hasher` alias could be misclassified; unordered containers without that alias will hash order-sensitively.

Test signals: Static assertions for `std::unordered_set/map`, ordered containers, and custom containers with/without `hasher`.
