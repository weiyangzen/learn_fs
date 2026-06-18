# sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_map_find.hpp

Purpose: Implements lookup of an entry by key in an MP11 map represented as a list of list-like entries.

Important APIs, types, and functions: `mp_map_find<M,K>` and internal `mp_map_find_impl`. GCC 14 workaround paths wrap entries to avoid compiler bug 120161.

Control flow: Normal implementation builds an overload set through inheritance from `mp_identity<T>` for each entry and overload resolution selects the entry whose front element matches `K`; missing keys yield `void`. Workaround path wraps tuples/lists before lookup and unwraps afterward.

State and persistence behavior: Compile-time only.

Dependencies and integration points: Used by `algorithm.hpp` for fallback `mp_at_c` and by MP11 map utilities.

Risks: Map entries must have key as front element. Duplicate keys select according to overload behavior and are not a runtime error. Workaround code is compiler-version sensitive.

Test signals: Static assertions for found/missing keys, tuple/list entries, duplicate-key expectations, and GCC workaround builds.
