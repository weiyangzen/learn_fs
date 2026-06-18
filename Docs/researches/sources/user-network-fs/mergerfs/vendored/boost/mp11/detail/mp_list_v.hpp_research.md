# sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_list_v.hpp

Purpose: Defines the fundamental MP11 value-list container for `template<auto...>` values.

Important APIs, types, and functions: `template<auto... A> struct mp_list_v`, available only when `BOOST_MP11_HAS_TEMPLATE_AUTO` is set.

Control flow: None; compile-time value wrapper.

State and persistence behavior: Compile-time value container only.

Dependencies and integration points: Used by value-list aware MP11 primitives such as `mp_append`, `mp_front`, and `mp_transform`.

Risks: Feature-gated; clients must not rely on it in pre-C++17/template-auto modes.

Test signals: Compile value-list algorithms with integral and enum values; ensure header is inert when template-auto support is unavailable.
