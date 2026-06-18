<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/abstract_mem.h -->
# sources/user-network-fs/nfs-ganesha/src/include/abstract_mem.h

## Purpose
`abstract_mem.h` provides Ganesha allocation shims and a minimal object-pool abstraction. It wraps libc allocation functions so allocator behavior can be swapped or instrumented while giving callers a consistent abort-on-OOM contract.

## Important APIs, types, and functions
- `gsh_malloc__()`, `gsh_calloc__()`, `gsh_realloc__()`, and `gsh_malloc_aligned__()` accept call-site metadata and log malloc failures before aborting.
- Simpler `gsh_malloc()`, `gsh_calloc`, `gsh_realloc()`, `gsh_strdup()`, `gsh_memdup()`, `gsh_free()`, and `gsh_free_size()` wrap libc operations with abort-on-failure behavior.
- `gsh_malloc_aligned(a, n)` uses `posix_memalign()` or Apple `valloc()` in the metadata form.
- `gsh_strdupa()` maps to glibc `strdupa()` when available or an `alloca()` plus copy fallback.
- `pool_t` records a pool name and object size.
- `pool_basic_init()`, `pool_destroy()`, `pool_alloc()`, and `pool_free()` implement a simple calloc/free based pool abstraction.
- `gsh_concat()` and `gsh_concat_sep()` allocate concatenated path/string buffers.

## Control flow
Allocation calls immediately abort on OOM rather than returning NULL, except `gsh_realloc()` accepts `n == 0` behavior. Pool creation allocates and names a pool object; `pool_alloc()` zero-allocates one object of the pool's size; `pool_free()` frees it. Callers release all returned memory with `gsh_free()` or the matching pool destroy/free function.

## State and persistence
The header itself has no global state. Pool objects hold name and object size, while allocated objects are ordinary heap memory. No allocations persist across process exit unless intentionally leaked by caller-owned lifecycle.

## Dependencies and integration points
It depends on libc allocation/string APIs, `assert.h`, `alloca()` availability through includers/toolchain, and Ganesha logging for metadata variants. It is included widely by Ganesha code and underlies cache entries, parsed strings, list nodes, and utility allocations.

## Risks
- Abort-on-OOM simplifies callers but prevents graceful degradation under memory pressure.
- Macro forms such as `gsh_calloc`, `gsh_malloc_aligned`, and `pool_alloc` evaluate arguments in expression contexts and may surprise debuggers or non-GNU compilers.
- `gsh_strdupa()` allocates on the stack; large inputs can overflow stack.
- Pool abstraction currently does not track outstanding objects despite comments requiring all objects be returned before destroy.
- `gsh_concat*()` assumes non-NULL inputs and can overflow `size_t` for extreme lengths.

## Test signals
- Allocation tests should cover normal malloc/calloc/realloc/strdup/memdup/free and aligned allocation alignment.
- Failure-injection builds should verify metadata variants log and abort as expected.
- Pool tests should create/destroy pools and ensure allocated objects are zeroed.
- Portability builds should cover glibc, non-glibc, Apple, and C++ include contexts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/abstract_mem.h -->
