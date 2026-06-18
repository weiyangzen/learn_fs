# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lzio.h

## Purpose

Declares buffered stream and memory-buffer structures used by the lexer/parser and binary chunk loader.

## Key Definitions

- `EOZ`: end-of-stream sentinel.
- `ZIO`: buffered reader state.
- `zgetc`: fast byte fetch macro.
- `Mbuffer`: growable temporary memory buffer.
- Buffer macros for init, access, length reset, resize, and free.

## APIs

- `luaZ_openspace`
- `luaZ_init`
- `luaZ_read`
- `luaZ_fill`

## Risks And Notes

- `zgetc` decrements `n` before checking; it relies on unsigned wrap behavior matching the macro’s intended fast path.
- `Mbuffer.n` is separate from allocated `buffsize`; callers must maintain logical length.
