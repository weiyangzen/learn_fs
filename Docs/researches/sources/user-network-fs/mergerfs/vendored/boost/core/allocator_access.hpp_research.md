# sources/user-network-fs/mergerfs/vendored/boost/core/allocator_access.hpp

Purpose: Backports allocator-traits style type discovery and operations for allocators across old and modern C++ modes.

Important APIs, types, and functions: Type traits for allocator value/pointer/const pointer/void pointer/difference/size types, propagation traits, `allocator_is_always_equal`, `allocator_rebind`, and alias templates. Operation helpers include `allocator_allocate`, `allocator_deallocate`, `allocator_construct`, `allocator_destroy`, `allocator_max_size`, `allocator_select_on_container_copy_construction`, `allocator_construct_n`, and `allocator_destroy_n`.

Control flow: SFINAE detects optional allocator members (`pointer`, `construct`, `destroy`, `max_size`, `select_on_container_copy_construction`, hinted `allocate`). Fallbacks use placement new, destructor calls, numeric limit max size, and allocator copy. Bulk construction uses `detail::alloc_destroyer` RAII so partially constructed ranges are destroyed on exception.

State and persistence behavior: No persistent global state. Temporary state is the `alloc_destroyer` count tracking constructed elements during a bulk operation.

Dependencies and integration points: Depends on `pointer_traits.hpp`, Boost config, `<limits>`, `<new>`, `<type_traits>`, and `<utility>`. Exposed through `allocator_traits.hpp`.

Risks: Old-compiler branches and deprecated allocator member detection are fragile. Construction fallback must preserve exception safety and forwarding semantics. Incorrect rebinding can break fancy-pointer allocators.

Test signals: Custom allocator with full traits, minimal allocator, allocator with fancy pointer, throwing element construction for cleanup, hinted allocate present/absent, and old C++ compatibility builds.
