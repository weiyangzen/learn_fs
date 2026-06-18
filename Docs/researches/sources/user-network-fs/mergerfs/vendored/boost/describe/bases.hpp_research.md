# sources/user-network-fs/mergerfs/vendored/boost/describe/bases.hpp

Purpose: Provides Boost.Describe base-class descriptor querying.

Important APIs, types, and functions: `describe_bases<T,M>`, `has_describe_bases<T>`, internal `_describe_bases<T>`, and `base_filter<M>`.

Control flow: For C++11-capable configurations, ADL probes `boost_base_descriptor_fn(static_cast<T**>(0))` and MP11 filters descriptor lists by requested access modifiers.

State and persistence behavior: Compile-time metadata only.

Dependencies and integration points: Depends on `modifiers.hpp`, `void_t.hpp`, config, MP11 algorithm, and type traits. Used by described-class hashing in `hash.hpp` and member inheritance traversal.

Risks: Requires generated/declared descriptor functions from Boost.Describe macros. Missing metadata produces SFINAE false rather than runtime failure.

Test signals: Static assertions for described and undescribed bases, modifier filtering, virtual base metadata, and C++03 disabled path.
