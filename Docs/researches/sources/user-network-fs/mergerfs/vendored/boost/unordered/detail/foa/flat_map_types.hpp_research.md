# sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/foa/flat_map_types.hpp

Purpose: Defines the type policy that adapts FOA table storage to flat map key/value semantics.

Important APIs, types, and functions: `flat_map_types<Key,T>` defines `key_type`, `mapped_type`, raw key/mapped types, `init_type`, `moved_type`, `value_type`, `element_type`, `constructibility_checker`, `value_from`, `extract`, `move`, `construct`, and `destroy`.

Control flow: `extract` returns `.first` from pair-like values. `move` converts mutable init or element pairs into rvalue key/mapped pairs, using `const_cast` to move from the stored `pair<Key const,T>`. Construction first runs map constructibility checks for standard allocators, then delegates to `boost::allocator_construct`; destruction delegates to allocator destroy.

State and persistence behavior: No state. It is a compile-time policy consumed by `table_core` and `concurrent_table`.

Dependencies and integration points: Depends on `types_constructibility.hpp` and allocator access. Used by `concurrent_flat_map` and unordered flat map internals.

Risks: Moving from a `const` key requires careful internal-only use while relocating elements. The TODO about laundering notes a potential object-model sensitivity.

Test signals: Tests should cover pair construction forms, piecewise construction, move relocation, non-copyable mapped values, and allocator construct diagnostics.
