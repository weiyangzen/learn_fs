# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lstrlib.c

## Purpose

Implements Lua’s standard `string` library for the ZFS-embedded Lua runtime.

## Library Functions

Registers:

- `string.byte`
- `string.char`
- `string.dump`
- `string.find`
- `string.format`
- `string.gmatch`
- `string.gsub`
- `string.len`
- `string.lower`
- `string.match`
- `string.rep`
- `string.reverse`
- `string.sub`
- `string.upper`

## Core Behavior

- Basic string functions operate on explicit byte lengths, not C-string length.
- Pattern matching implements Lua patterns with captures, balanced matches `%b`, frontier `%f`, back references, greedy/minimal repetitions, and recursion-depth protection.
- `find` uses a plain byte search when requested or when the pattern contains no special characters.
- `gmatch` returns a closure over source, pattern, and current byte offset.
- `gsub` supports string/number replacements, function replacements, and table lookups.
- `format` scans restricted printf-style format specifiers, supports quoted `%q`, integer formats, string formats, and conditionally floating formats depending on build macros.
- `luaopen_string` creates the library table and installs it as the metatable `__index` for strings.

## illumos/ZFS Adaptations

- Includes `<sys/ctype.h>` and `<sys/zfs_context.h>`.
- Adds local `tolower`, `toupper`, `isgraph`, and `ispunct` macros.
- Adds local `iscntrl`.
- Uses `str_sprintf` wrapper over `vsnprintf` because the available `sprintf` compatibility function does not match the expected return type.

## Dependencies

- Public Lua API: `lua.h`.
- Auxiliary library and standard-library registration: `lauxlib.h`, `lualib.h`.

## Risks And Notes

- Pattern matching uses recursive calls bounded by `MAXCCALLS`; complex patterns throw `"pattern too complex"`.
- Capture storage is fixed at `LUA_MAXCAPTURES` default 32.
- `str_rep`, `str_byte`, and `unpack`-style result pushing guard against overflow/stack exhaustion.
- Character classification is ASCII-oriented in the patched macros.
