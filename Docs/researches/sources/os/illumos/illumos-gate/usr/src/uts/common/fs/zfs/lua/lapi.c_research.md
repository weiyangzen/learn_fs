# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lapi.c

## Role

`lapi.c` implements the public Lua C API entry points used by embedders and Lua libraries. It is the main bridge between external C callers and the internal Lua VM objects, stack frames, tables, closures, coroutines, parser, dumper, allocator, and garbage collector.

## Main Responsibilities

- Converts API stack indexes, including positive stack indexes, negative relative indexes, registry indexes, and C-closure upvalue pseudo-indexes, into internal `TValue *` addresses.
- Implements stack manipulation: `lua_checkstack`, `lua_xmove`, `lua_absindex`, `lua_gettop`, `lua_settop`, `lua_remove`, `lua_insert`, `lua_replace`, `lua_copy`, and `lua_pushvalue`.
- Implements C-to-Lua and Lua-to-C value access: type tests, numeric/string/userdata/thread/pointer conversions, raw length, raw equality, arithmetic, and comparison.
- Implements push APIs for nil, numbers, integers, unsigned values, strings, formatted strings, C closures, booleans, light userdata, and current thread.
- Implements table/global/userdata/metatable accessors and mutators, including raw table operations and write-barrier calls after storing collectable objects.
- Implements calls, protected calls, continuations, loading, dumping, status queries, GC control, table iteration, concatenation, object length, userdata allocation, allocator replacement, and upvalue inspection/mutation/joining.

## Integration Points

The file depends on almost every Lua core subsystem: `ldo` for calls/protected execution, `lvm` for table/arithmetic/metamethod operations, `lstring` and `ltable` for objects, `lgc` for barriers and GC stepping, `lundump` for binary chunks, and `lfunc` for closures/upvalues.

## Risk Notes

API correctness depends on stack-index validation, frame-top adjustment, and GC barriers. The `moveto`, raw table setters, metatable setters, userdata environment setters, load upvalue initialization, and upvalue APIs are especially sensitive because stale barriers or invalid pseudo-index handling can corrupt the incremental collector or closure state.
