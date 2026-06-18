# sources/user-network-fs/mergerfs/vendored/boost/core/allocator_traits.hpp

Purpose: Public `boost::allocator_traits` facade over the lower-level allocator access helpers.

Important APIs, types, and functions: `allocator_traits<A>` exposes standard allocator typedefs, `rebind_traits`, and static `allocate`, `deallocate`, `construct`, `destroy`, `max_size`, and `select_on_container_copy_construction`.

Control flow: Each static member forwards directly to the matching `boost::allocator_*` helper, inheriting that helper's SFINAE/fallback behavior.

State and persistence behavior: Stateless traits facade.

Dependencies and integration points: Includes `allocator_access.hpp`. Used by containers or utilities that want a Boost-provided allocator-traits interface independent of standard library support.

Risks: Must remain a thin alias-compatible facade; mismatches with `allocator_access` typedefs or forwarding overloads can affect allocator-aware containers.

Test signals: Compile with minimal and custom allocators; verify `rebind_traits`; exercise construction/destruction and max-size forwarding against `allocator_access` behavior.
