# sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_is_value_list.hpp

Purpose: Detects whether a type is an instantiation of a template-auto value list.

Important APIs, types, and functions: `mp_is_value_list<L>`.

Control flow: Primary template returns false; when `BOOST_MP11_HAS_TEMPLATE_AUTO` is available, `template<auto...>` specializations return true.

State and persistence behavior: Compile-time only.

Dependencies and integration points: Used by `mp_append` to choose value-list concatenation.

Risks: Disabled entirely on compilers without template-auto support. Mixed lists require careful algorithm selection.

Test signals: Static assertions for `mp_list_v<...>`, type lists, non-list types, and feature-disabled builds.
