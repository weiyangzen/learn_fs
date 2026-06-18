# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lstring.c

## Purpose

Implements Lua string hashing, short-string interning, long-string creation/equality, string-table resizing, and userdata allocation.

## Main APIs

- `luaS_hash`: seeded hash over a bounded sample of string bytes.
- `luaS_eqlngstr`, `luaS_eqstr`: long/general string equality.
- `luaS_resize`: resize and rehash the interned short-string table.
- `luaS_newlstr`, `luaS_new`: create strings.
- `luaS_newudata`: allocate userdata with environment/metatable fields.

## Core Behavior

- Short strings up to `LUAI_MAXSHORTLEN` are interned and reused.
- Long strings are not interned; equality compares length and content.
- Dead short strings found during lookup are resurrected with `changewhite`.
- String-table resize waits until GC is not in string-sweep state and resets old bits during rehash.
- New string objects store a trailing NUL after explicit-length payloads.

## Dependencies

- GC object allocation: `lgc.h`.
- Memory helpers: `lmem.h`.
- State/string table: `lstate.h`.

## Risks And Notes

- Hashing samples at most roughly `2^LUAI_HASHLIMIT` bytes, so adversarial long strings rely on randomized seed for mitigation.
- Short-string interning assumes the string table has already been initialized by `luaS_resize`.
- Long-string hash is initially the global seed and may be lazily computed elsewhere for table hashing.
