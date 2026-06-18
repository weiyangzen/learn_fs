# sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/foa/types_constructibility.hpp

Purpose: Supplies targeted static assertions for map/set key and mapped type construction when FOA containers use `std::allocator`.

Important APIs, types, and functions: Defines `check_key_type_t`, `check_mapped_type_t`, `map_types_constructibility<TypePolicy>`, and `set_types_constructibility<TypePolicy>`.

Control flow: General allocator overloads are no-ops because custom allocators may provide construction semantics not visible to type traits. `std::allocator<value_type>` overloads validate direct, pair, rvalue pair, and piecewise construction forms for keys and mapped values. Set policy asserts `key_type == value_type` and checks key constructibility.

State and persistence behavior: Compile-time-only; no objects or runtime state.

Dependencies and integration points: Used by `flat_map_types` before allocator construction, improving diagnostics for `concurrent_flat_map` and other FOA map/set containers.

Risks: Custom allocators bypass these checks, so diagnostics may occur later inside allocator construction. Trait checks must match the construction forms used by table policies.

Test signals: Compile-fail tests should cover non-copyable/non-movable keys, non-default-constructible mapped values for `try_emplace`, pair and piecewise construction, and custom allocator bypass behavior.
