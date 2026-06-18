# sources/user-network-fs/mergerfs/vendored/boost/container_hash/is_contiguous_range.hpp

Purpose: Identifies range types whose elements can be hashed through contiguous memory via `data()` and `size()`.

Important APIs, types, and functions: Public `boost::container_hash::is_contiguous_range<T>`. Modern compilers use SFINAE to compare `begin/end` with `data/data+size`; old MSVC fallback specializes strings, vectors except `vector<bool>`, and arrays.

Control flow: Compile-time detection only. The trait gates the optimized `hash_value` overload in `hash.hpp`.

State and persistence behavior: No state.

Dependencies and integration points: Depends on `is_range.hpp`, Boost config/workaround headers, `<type_traits>`, and optionally standard containers. Integrates with `hash_range` byte fast paths.

Risks: Custom contiguous containers must satisfy the exact member expression pattern. False positives could hash memory with the wrong extent; false negatives fall back to element iteration. `vector<bool>` is explicitly non-contiguous for value hashing.

Test signals: Static assertions for `std::string`, `std::vector<int>`, `std::vector<bool>`, `std::array<T,N>`, const-qualified variants, and custom containers.
