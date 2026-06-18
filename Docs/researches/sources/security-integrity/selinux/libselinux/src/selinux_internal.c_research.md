<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/selinux_internal.c -->
# sources/security-integrity/selinux/libselinux/src/selinux_internal.c

## Purpose
Provides portability fallbacks for libc functions that may be absent on target platforms.

## Important APIs, Types, And Functions
Defines `strlcpy()` when `HAVE_STRLCPY` is absent and `reallocarray()` when `HAVE_REALLOCARRAY` is absent.

## Control Flow
`strlcpy()` copies up to `size - 1` bytes and always NUL-terminates when size is nonzero. `reallocarray()` checks multiplication overflow before calling `realloc()`.

## State And Persistence Behavior
No persistent state.

## Dependencies And Integration Points
Shared by code using safer string copy and overflow-checked allocation, especially path and dynamic-array logic.

## Risks And Test Signals
Tests should cover zero-size `strlcpy`, truncation return values, exact fit, `reallocarray()` overflow, zero-sized allocation, and normal allocation.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/selinux_internal.c -->
