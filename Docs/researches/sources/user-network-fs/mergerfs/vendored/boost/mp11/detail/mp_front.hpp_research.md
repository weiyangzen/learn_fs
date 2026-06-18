# sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_front.hpp

Purpose: Implements `mp_front`, retrieving the first element of a type or value list.

Important APIs, types, and functions: `detail::mp_front_impl<L>` and public alias `mp_front<L>`. Value-list support wraps the first value in `mp_value<A>`.

Control flow: Template specialization matches non-empty list templates; empty/non-list inputs intentionally lack `type`.

State and persistence behavior: Compile-time only.

Dependencies and integration points: Used by algorithms such as fold, min/max, map find, sort, and bind.

Risks: Empty list use is a hard compile error by design; value-list behavior depends on template-auto support.

Test signals: Static assertions for `mp_list<T...>`, standard tuple-like type lists, value lists, and compile-fail empty list behavior.
