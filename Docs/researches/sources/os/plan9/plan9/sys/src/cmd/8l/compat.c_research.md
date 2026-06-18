# File Research: sources/os/plan9/plan9/sys/src/cmd/8l/compat.c

Purpose: compatibility allocation and filesystem helpers for the linker.

Key behavior: implements a bump-pointer `malloc` over linker hunks, no-op `free`, zeroing `calloc`, aborting `realloc`, `mysbrk`, no-op `setmalloctag`, and `fileexists`.

Integration notes: linker code assumes arena allocation and does not support general realloc/free behavior. `fileexists` is used for library path and `$ccroot` validation.
