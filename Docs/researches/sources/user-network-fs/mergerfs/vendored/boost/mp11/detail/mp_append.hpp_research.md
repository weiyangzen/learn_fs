# sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_append.hpp

Purpose: Implements `mp_append`, the foundational list concatenation primitive for type and value lists.

Important APIs, types, and functions: Internal `mp_append_impl`, `append_11_impl`, `append_value_impl`, `append_type_lists`, `append_value_lists`, and public alias `mp_append<L...>`.

Control flow: Template specializations concatenate list packs, batching groups of up to eleven lists to reduce instantiation depth. With template-auto support, value-list concatenation is selected when all inputs are value lists; otherwise type-list concatenation is used.

State and persistence behavior: Compile-time only.

Dependencies and integration points: Used throughout MP11 algorithms, Describe metadata accumulation, and ContainerHash described-class support.

Risks: Mixed type/value lists are intentionally not value-concatenated. Compiler workaround branches for MSVC and CUDA must preserve behavior.

Test signals: Static assertions for zero/one/many lists, large list batches, value-list concatenation, mixed list rejection/typing, and old compiler workaround builds.
