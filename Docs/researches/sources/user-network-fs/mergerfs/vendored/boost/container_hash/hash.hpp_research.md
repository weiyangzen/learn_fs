# sources/user-network-fs/mergerfs/vendored/boost/container_hash/hash.hpp

Purpose: Main Boost.ContainerHash public implementation. It defines `boost::hash`, `hash_value` overloads for common C++ types, `hash_combine`, ordered/unordered range hashing, and conditional support for described classes, smart pointers, optional, variant, string view, system errors, and type indices.

Important APIs, types, and functions: `hash_value` overloads for enums, floating point, pointers, arrays, `std::complex`, `std::pair`, ranges, contiguous ranges, unordered ranges, described classes, smart pointers, `std::type_index`, `std::error_code`, `std::nullptr_t`, `std::optional`, `std::variant`, and `std::monostate`; public `hash_combine`, `hash_range`, `hash_unordered_range`; class template `boost::hash<T>`; specializations of `hash_is_avalanching` for strings/string views.

Control flow: Hash dispatch is overload/SFINAE driven. Floating point values are copied into integer words and normalized with `v + 0` to collapse negative zero. Ordered ranges combine sequentially; unordered ranges hash each element against the original seed and add commutatively. Described classes iterate base and member descriptors with MP11.

State and persistence behavior: Stateless header-only algorithms. Hash values are deterministic for a build/configuration but pointer/category-based hashes can vary by process and platform.

Dependencies and integration points: Central integration point for `hash_fwd`, range traits, tuple-like hashing, Boost.Describe, Boost.MP11, and standard library type support. mergerfs inherits this behavior through its vendored Boost include tree.

Risks: Hash output changes can affect container behavior, tests, and serialized hash assumptions. Pointer hashing depends on addresses; error category hashing uses category addresses; optional and monostate use arbitrary constants. Described unions are rejected by static assertion.

Test signals: Compile across C++03 through C++17 feature sets; verify known hashes for primitive, floating, string, vector, unordered set, tuple-like, optional, and variant inputs; test described class hashing with inherited members; check ADL `hash_value` extension behavior.
