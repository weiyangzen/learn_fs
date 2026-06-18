# sources/user-network-fs/mergerfs/vendored/libfuse/lib/xalloc.hpp

## Purpose
`xalloc.hpp` provides fatal allocation helpers that include source file and line information in error messages.

## Important APIs, Types, and Functions
Macros `xstrdup(S)` and `xmalloc(S)` expand to `xstrdup_impl` and `xmalloc_impl` with `__FILE__` and `__LINE__`. `xstrdup_impl` rejects null input and failed `strdup`; `xmalloc_impl` exits on failed `malloc`.

## Control Flow
Callers invoke the macros where allocation is considered unrecoverable. On invalid/null input or allocation failure, the helper prints a mergerfs-prefixed diagnostic to stderr and exits `EXIT_FAILURE`. On success, it returns the allocated pointer.

## State and Persistence
No state is held. Returned memory ownership belongs to the caller.

## Dependencies and Integration Points
The header depends on stdio/stdlib and is used by `fuse.cpp` for root node name allocation. It can be included anywhere a fail-fast allocation policy is acceptable.

## Risks
These helpers terminate the process instead of returning errors, so they should not be used in paths where libfuse is expected to recover from ENOMEM. `xmalloc(0)` behavior follows libc `malloc(0)` and may abort on null.

## Test Signals
Test null `xstrdup`, forced allocation failure, diagnostic file/line accuracy, and caller ownership/free behavior.
