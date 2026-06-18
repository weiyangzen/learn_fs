# File Research: sources/os/bsd/dragonflybsd/sys/sys/objcache.h

Kernel object cache allocator interface with pluggable backing allocator and statistics ABI.

Key responsibilities:
- Defines object constructor, destructor, allocation, and free function pointer types.
- Declares object cache creation helpers for generic, simple malloc-backed, and configurable malloc-backed caches.
- Declares APIs to set cluster limits, get/put objects, run destructor, prepopulate from a linear object area, reclaim cache lists, and destroy caches.
- Defines common malloc-backed allocator argument structure.
- Declares malloc, zeroing malloc, and no-op backing alloc/free helpers.
- Defines stats constants and public `struct objcache_stats`.

Important behavior:
- `OC_MFLAGS` reserves low bits for malloc-style flags.
- Constructors return `bool`, allowing acquisition failure or rejection.
- `OBJCACHE_UNLIMITED` is represented as a high sentinel in stats limits.

Dependencies:
- Includes `sys/types.h`; kernel structures include `_malloc.h`.
- Kernel APIs depend on `malloc_type_t` and object-cache implementation.

Notable risks:
- Constructor/destructor semantics differ from backing allocator semantics; callers must know when object state is initialized or torn down.
- Stats structure is public/user-visible and includes reserved zero fields for future expansion.
