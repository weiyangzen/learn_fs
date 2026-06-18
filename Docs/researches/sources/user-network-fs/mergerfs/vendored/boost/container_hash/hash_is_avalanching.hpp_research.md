# sources/user-network-fs/mergerfs/vendored/boost/container_hash/hash_is_avalanching.hpp

Purpose: Detects whether a hash function type advertises avalanching behavior.

Important APIs, types, and functions: `hash_is_avalanching<Hash>` public trait; internal `void_t`, `avalanching_value`, and `hash_is_avalanching_impl`. It supports both nested type `Hash::is_avalanching` and static data member `Hash::is_avalanching`; nested `void` is treated as true for legacy compatibility.

Control flow: Pure SFINAE trait selection at compile time.

State and persistence behavior: No state.

Dependencies and integration points: Included by `hash.hpp` and used by unordered/container code to identify quality of hash functions.

Risks: Treating nested `void` as true is compatibility behavior that can mask imprecise declarations. Static data member probing may instantiate surprising expressions for unusual hash types.

Test signals: Static assertions for no marker, nested `std::true_type`, nested `std::false_type`, nested `void`, and static constexpr bool markers.
