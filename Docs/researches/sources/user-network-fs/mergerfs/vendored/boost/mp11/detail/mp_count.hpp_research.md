# sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_count.hpp

Purpose: Implements compile-time element counting and predicate counting.

Important APIs, types, and functions: `mp_count<L,V>`, `mp_count_if<L,P>`, `mp_count_if_q<L,Q>`, and constexpr helpers `cx_plus`, `cx_count`, `cx_count_if`.

Control flow: Preferred implementations use constexpr bool arrays and loops or recursive constexpr addition; fallback uses `mp_plus` over boolean integral constants.

State and persistence behavior: Compile-time only.

Dependencies and integration points: Used by MP11 algorithms, `mp_append` value-list selection, and logical predicates.

Risks: Compiler constexpr support changes implementation. Predicate values must be convertible to bool.

Test signals: Static assertions for duplicates, missing elements, empty lists, predicate counts, large lists, and no-constexpr fallback builds.
