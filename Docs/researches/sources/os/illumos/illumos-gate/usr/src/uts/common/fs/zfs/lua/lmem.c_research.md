# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lmem.c

## Role

`lmem.c` implements Lua's memory manager interface around the configured allocator.

## Main Responsibilities

- Grows dynamic arrays with doubling up to a limit, enforcing minimum array size and reporting limit errors by object type.
- Reports oversized allocations with a Lua runtime error.
- Implements `luaM_realloc_`, including allocator invocation, emergency full-GC retry on allocation failure, shrink invariants, memory-error throwing, and GC debt accounting.

## Integration Points

All runtime allocation macros in `lmem.h` route to this implementation. It calls into `lgc` for emergency collection and `ldo` for memory-error throws.

## Risk Notes

The allocator contract is strict: shrinking cannot fail, freeing returns `NULL`, and allocation failures throw `LUA_ERRMEM`. GC debt accounting drives collector pacing.
