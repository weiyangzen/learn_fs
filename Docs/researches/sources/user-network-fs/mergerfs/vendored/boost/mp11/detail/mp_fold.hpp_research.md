# sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_fold.hpp

Purpose: Implements left fold over MP11 lists.

Important APIs, types, and functions: `mp_fold<L,V,F>`, `mp_fold_q<L,V,Q>`, `mp_fold_impl`, and unrolled helper structs `mp_fold_Q1` through `mp_fold_Q9`.

Control flow: Converts input to `mp_list`, handles empty list as initial value, unrolls up to nine elements, and recursively folds groups of ten for longer lists to manage instantiation depth.

State and persistence behavior: Compile-time accumulator type only.

Dependencies and integration points: Used by MP11 min/max, unique, partial sums, Describe inherited metadata processing, and many algorithms.

Risks: Metafunction `F` must accept accumulator and element in the expected order. Very large lists can still stress compiler template depth.

Test signals: Static assertions for empty, single, short, and long lists; quote variant; accumulator order; old MSVC workaround mode.
