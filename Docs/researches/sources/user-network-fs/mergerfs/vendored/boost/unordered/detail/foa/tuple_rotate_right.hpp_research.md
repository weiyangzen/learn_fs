# sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/foa/tuple_rotate_right.hpp

Purpose: Provides a small tuple utility for rotating variadic argument packs so callback arguments can be moved to the front for internal dispatch.

Important APIs, types, and functions: Defines `tuple_rotate_right_return_type<Offset,Tuple>`, `tuple_rotate_right_aux`, and `tuple_rotate_right<Offset=1>`.

Control flow: Uses MP11 index sequences and `mp_rotate_right_c` to construct a tuple whose elements are fetched from `(Is + size - Offset) % size`, preserving forwarding.

State and persistence behavior: No persistent state; returns a new tuple value.

Dependencies and integration points: Used by `concurrent_table` to rearrange variadic `emplace_or_visit` and `emplace_and_visit` calls where callback arguments are syntactically last but internal helpers want them earlier.

Risks: Requires non-empty tuple types for modulo arithmetic. Forwarding through tuple construction can affect value categories according to tuple rules.

Test signals: Unit tests should rotate tuples of lvalues/rvalues and offsets 1 and 2, matching concurrent table callback dispatch patterns.
