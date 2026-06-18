<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_malloc.c -->
# sources/user-network-fs/samba/source3/lib/util_malloc.c

## Purpose
`util_malloc.c` provides Samba allocation wrappers, including optional paranoid wrappers that prevent direct malloc/realloc usage and a `Realloc` helper with explicit old-pointer ownership behavior.

## Important APIs, types, and functions
Under `PARANOID_MALLOC_CHECKER`, `malloc_` and internal `realloc_` call the real libc functions while macros poison direct calls. Public `Realloc` expands or frees memory depending on `size` and `free_old_on_error`.

## Control flow
`Realloc` returns NULL for zero size and optionally frees the old pointer. For nonzero size it calls malloc or realloc, using paranoid wrappers when enabled. On allocation failure it optionally frees the old pointer and logs an error.

## State and persistence behavior
No persistent state is used. The function's key state effect is whether it frees the input pointer on failure or zero size.

## Dependencies and integration points
It depends on Samba memory macros, debug logging, and build-time `PARANOID_MALLOC_CHECKER`. Legacy code uses it through `SMB_REALLOC`-style macros.

## Risks and edge cases
The ownership mode is critical: using the freeing variant in code that expects to preserve old contents can cause use-after-free. Zero-size requests are treated as errors/logged and may free the pointer.

## Test signals
Tests should cover NULL input, successful resize, zero-size behavior for both ownership modes, simulated allocation failure, and paranoid checker builds.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_malloc.c -->
