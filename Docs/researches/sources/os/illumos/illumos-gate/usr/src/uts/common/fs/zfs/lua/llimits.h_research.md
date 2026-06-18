# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/llimits.h

## Role

`llimits.h` centralizes Lua's internal limits, memory-size types, casts, assertions, stack/call limits, instruction type, number conversion helpers, locking hooks, and hard-test hooks.

## Main Responsibilities

- Defines `lu_int32`, `lu_mem`, `l_mem`, `lu_byte`, memory maxima, `MAX_INT`, pointer hashing conversion, and alignment type.
- Defines internal and API assertion helpers, casts, unused markers, and `l_noret`.
- Sets `LUAI_MAXCCALLS` to 20 in this tree, with a comment noting amd64 stack-margin concerns.
- Defines `MAXUPVAL`, `Instruction`, `MAXSTACK`, minimum string-table size, and minimum scanner buffer size.
- Provides default no-op locking/yield/userstate hooks.
- Implements or selects number-to-integer/unsigned conversions and unsigned-to-number conversion.
- Routes numeric hashing through `lcompat_hashnum` when compiling table code and no other `luai_hashnum` is defined.
- Defines `condmovestack` and `condchangemem` hard-test hooks.

## Integration Points

Included by nearly all internal Lua headers. It adapts the upstream Lua runtime to illumos/ZFS kernel constraints through headers, call-depth limits, and compatibility hooks.

## Risk Notes

Build-wide numeric and stack assumptions live here. The low `LUAI_MAXCCALLS` is a deliberate safety bound; raising it can increase kernel stack risk. Numeric conversion and hashing settings affect table key behavior.
