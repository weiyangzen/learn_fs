# sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_copy_if.hpp

Purpose: Implements `mp_copy_if`, filtering a list by predicate while preserving the original list template.

Important APIs, types, and functions: `detail::mp_copy_if_impl`, public `mp_copy_if<L,P>`, and `mp_copy_if_q<L,Q>`.

Control flow: For each element, template `_f` maps matching elements to singleton `mp_list<U>` and nonmatches to `mp_list<>`; `mp_append` then flattens the results into the output list.

State and persistence behavior: Compile-time only.

Dependencies and integration points: Used by MP11 algorithms and Boost.Describe descriptor filtering.

Risks: Predicate must expose a boolean `value`. Old MSVC branch uses nested `::type` indirection.

Test signals: Static assertions for empty lists, all/none/some matches, quote variants, and preserving list template.
