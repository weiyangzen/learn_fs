# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lmem.h

## Role

`lmem.h` defines allocation, free, reallocation, vector growth, and overflow-checking macros for the Lua core.

## Main Responsibilities

- Provides `luaM_reallocv` with element-count overflow checking.
- Defines macros for freeing memory/arrays, allocating objects/vectors, growing vectors, and reallocating vectors.
- Declares `luaM_toobig`, `luaM_realloc_`, and `luaM_growaux_`.

## Integration Points

Used by nearly every file that allocates dynamic runtime structures: prototypes, bytecode arrays, strings, tables, stacks, parser buffers, and GC objects.

## Risk Notes

The overflow check protects `n * element_size` calculations. Callers must pass correct old sizes so allocator accounting and frees remain valid.
