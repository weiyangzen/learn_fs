# sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_min_element.hpp

Purpose: Implements minimum and maximum element selection over MP11 lists using a comparator predicate.

Important APIs, types, and functions: `mp_min_element<L,P>`, `mp_min_element_q`, `mp_max_element<L,P>`, `mp_max_element_q`, and internal `select_min`/`select_max` fold functors.

Control flow: Starts with `mp_first<L>` and folds over `mp_rest<L>`, replacing the current best when predicate comparison indicates a smaller/larger element.

State and persistence behavior: Compile-time accumulator type only.

Dependencies and integration points: Used by MP11 function utilities and algorithms such as min/max.

Risks: Empty lists are invalid because `mp_first`/`mp_rest` require elements. Comparator must expose boolean `value` and be strict enough for predictable selection.

Test signals: Static assertions for integer constants, custom comparators, quote variants, single-element lists, and compile-fail empty list behavior.
