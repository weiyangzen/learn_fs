# sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_list.hpp

Purpose: Defines the fundamental MP11 type-list container.

Important APIs, types, and functions: `template<class... T> struct mp_list`.

Control flow: None; it is an empty variadic type wrapper.

State and persistence behavior: Compile-time type container only.

Dependencies and integration points: Used throughout MP11 and Boost.Describe metadata lists.

Risks: No direct risks beyond preserving the empty-list type identity expected by algorithms.

Test signals: Static assertions that algorithms accept and preserve `mp_list` shape.
