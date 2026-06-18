# sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_is_list.hpp

Purpose: Detects whether a type is an instantiation of a type-template list.

Important APIs, types, and functions: `mp_is_list<L>`.

Control flow: Primary template returns `mp_false`; specialization for `template<class...> class L, class... T` returns `mp_true`.

State and persistence behavior: Compile-time only.

Dependencies and integration points: Used by MP11 list utilities and validation paths.

Risks: Value lists are not type lists; fixed-arity templates may not match unless expressible as variadic template patterns.

Test signals: Static assertions for `mp_list`, `std::tuple`, non-list types, and value-list types.
