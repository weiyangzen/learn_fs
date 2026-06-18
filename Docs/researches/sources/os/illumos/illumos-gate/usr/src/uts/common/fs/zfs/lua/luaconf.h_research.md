# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/luaconf.h

## Purpose

Configures the embedded Lua build for illumos/ZFS.

## Important Local Adaptations

- Includes `<sys/zfs_context.h>` and `<sys/int_fmtio.h>`.
- Declares compatibility helpers:
  - `lcompat_sprintf`
  - `lcompat_strtoll`
  - `lcompat_pow`
- Uses `zfs_dbgmsg` for `luai_writestringerror` when `_KERNEL` is defined.
- Defines `LUA_NUMBER` as `int64_t`, not `double`.
- Defines numeric parsing/formatting through `lcompat_strtoll` and `lcompat_sprintf`.
- Defines `LUA_UNSIGNED` as `uint64_t`.
- Forces locale decimal point to `'.'`.
- Supplies local `abs` and `UCHAR_MAX` fallback definitions.

## Core Configuration

- Default Lua module paths and C module paths are retained for non-Windows builds.
- `LUA_API` defaults to `extern`; internal symbols may use ELF hidden visibility under GCC/ELF.
- `LUAI_MAXSHORTLEN` is 40.
- `LUAI_MAXSTACK` is 1,000,000 on 32-bit-or-larger `int`.
- `LUAL_BUFFERSIZE` is 1024.
- Compatibility macros are available when `LUA_COMPAT_ALL` is defined.

## Numeric Semantics

- Arithmetic macros operate on integral `int64_t` Lua numbers.
- `%` is integer modulo.
- Power calls `lcompat_pow`.
- `lua_number2str` formats with `PRId64`.

## Risks And Notes

- Integer `lua_Number` is a major behavioral difference from stock Lua 5.2’s typical `double` configuration.
- Binary chunks are ABI-sensitive; `lundump.c` validates `sizeof(lua_Number)` and whether it is integral.
- Floating `string.format` support is conditional and may be unavailable unless configured.
