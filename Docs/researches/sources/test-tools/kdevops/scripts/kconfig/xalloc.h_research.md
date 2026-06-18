# sources/test-tools/kdevops/scripts/kconfig/xalloc.h

## Purpose
`xalloc.h` defines fail-fast allocation wrappers for the Kconfig code. These wrappers remove repetitive null checks by exiting the process on allocation failure.

## Important APIs, Types, And Functions
Static inline functions are `xmalloc()`, `xcalloc()`, `xrealloc()`, `xstrdup()`, and `xstrndup()`.

## Control Flow
Each wrapper calls the corresponding libc allocation/string duplication function, checks for null, calls `exit(1)` on failure, and otherwise returns the allocated pointer.

## State And Persistence
No state is stored. Allocations are caller-owned unless intentionally process-lifetime interned elsewhere.

## Dependencies And Integration Points
Includes `<stdlib.h>` and `<string.h>`. Used throughout the vendored Kconfig implementation.

## Risks And Edge Cases
Fail-fast behavior is simple but prevents graceful cleanup or detailed diagnostics on OOM. `xrealloc(ptr, 0)` inherits libc-specific behavior and may exit if it returns null. Consumers must still avoid integer overflows when calculating sizes.

## Test Signals
Compile coverage is usually sufficient. Fault-injection allocation tests can verify exit behavior if the project has an allocation shim.
