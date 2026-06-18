# File Research: sources/os/linux/linux-stable/fs/orangefs/orangefs-cache.c

## Scope

This file implements the slab cache and tag allocation for OrangeFS kernel operations.

## APIs Covered

- Cache lifecycle: `op_cache_initialize()`, `op_cache_finalize()`.
- Operation allocation: `op_alloc()`, `op_release()`.
- Tag assignment: `orangefs_new_tag()`.
- Debug naming: `get_opname_string()`.

## Control Flow And Behavior

- The operation cache is created with a usercopy-safe region spanning tag through upcall data.
- Tags start at 100, increment under spinlock, and wrap from zero back to 100.
- `op_alloc()` zeroes the operation, initializes list/lock/completion, sets invalid initial upcall/downcall types, assigns tag/type, and captures current fsuid/fsgid into the upcall.
- `get_opname_string()` maps all known VFS op codes to stable debug strings.

## Risks And Invariants

- Operation objects are protocol objects copied to/from userspace, so cache usercopy bounds are part of the security contract.
- Tags identify downcalls; reuse is only safe after previous op lifetime ends.
