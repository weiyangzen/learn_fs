# sources/user-network-fs/mergerfs/vendored/boost/container_hash/is_described_class.hpp

Purpose: Detects Boost.Describe-enabled class types that can be automatically hashed by member/base reflection.

Important APIs, types, and functions: Public `boost::container_hash::is_described_class<T>`, implemented as an integral constant over `boost::describe::has_describe_bases<T>` and `has_describe_members<T>`.

Control flow: Compile-time trait evaluation only.

State and persistence behavior: No state.

Dependencies and integration points: Depends on Boost.Describe bases and members headers plus `<type_traits>`. Used by `hash.hpp` to enable described-class `hash_value`.

Risks: A type needs both describe-bases and describe-members support; partial reflection metadata will not enable auto hashing. Unions are later rejected in `hash.hpp`.

Test signals: Static assertions for described struct/class, undescribed class, described union rejection through `hash_value`, and classes with inherited described bases.
