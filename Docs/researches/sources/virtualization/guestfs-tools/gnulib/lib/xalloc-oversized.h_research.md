# File Research: sources/virtualization/guestfs-tools/gnulib/lib/xalloc-oversized.h

Allocation overflow detection macro.

Exports:
- `xalloc_oversized(n, s)`

Behavior:
- Returns true if `n * s` would overflow size calculations or exceed reliable pointer-difference bounds.
- Uses compiler builtins for GCC where available.
- Falls back to division-based overflow checks.

Research relevance: guards array allocation sizing, notably in the hash table.
