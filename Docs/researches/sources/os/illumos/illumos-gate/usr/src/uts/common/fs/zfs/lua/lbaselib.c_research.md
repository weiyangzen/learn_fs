# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lbaselib.c

## Role

`lbaselib.c` implements the base Lua library exposed to ZFS channel programs, with several standard Lua functions deliberately removed.

## Main Responsibilities

- Provides base functions: `assert`, `collectgarbage`, `error`, `getmetatable`, `ipairs`, `next`, `pairs`, `rawequal`, `rawlen`, `rawget`, `rawset`, `select`, `setmetatable`, `tonumber`, `tostring`, and `type`.
- Registers `_G` and `_VERSION` in the global table via `luaopen_base`.
- Implements `tonumber` with optional base conversion from 2 through 36, including whitespace and sign handling.
- Implements protected metatable behavior through `__metatable`.
- Implements `pairs` and `ipairs`, honoring `__pairs` and `__ipairs` metamethods when present.
- Exposes GC controls through `collectgarbage`.

## Local/ZFS Adaptation

The file explicitly removes `dofile`, `loadfile`, `load`, `pcall`, `print`, and `xpcall` for ZFS channel programs. It also includes illumos/ZFS headers and local character handling.

## Risk Notes

The exposed base library is part of the sandbox surface. Reintroducing removed functions would materially change channel-program capabilities. The `collectgarbage` function gives scripts control over collector mode and pacing.
