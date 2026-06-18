# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/ldebug.c

## Role

`ldebug.c` implements Lua's debug interface, hook configuration, stack/local/upvalue inspection, debug information retrieval, symbolic bytecode analysis for names, and runtime error construction.

## Main Responsibilities

- Supports debug hooks for calls, returns, lines, and counts through `lua_sethook` and related getters.
- Implements `lua_getstack`, `lua_getlocal`, `lua_setlocal`, and `lua_getinfo`.
- Handles yielded call frames by swapping `CallInfo.extra` and `func` when needed.
- Builds function metadata: source, line ranges, current line, parameters, vararg status, tail-call status, active line table, and function objects.
- Symbolically scans bytecode to infer local/global/field/upvalue/method/metamethod names for better error messages.
- Implements type, concatenation, arithmetic, ordering, and generic runtime error reporting with source-line prefixes.
- Invokes error handlers through `luaG_errormsg`.

## Integration Points

The VM, API, auxiliary library, and call layer use this file for diagnostics and error throwing. It depends on opcode metadata, function prototypes, stack frames, tables, strings, and metamethod names.

## Risk Notes

Most code is diagnostic, but it runs during errors and hooks, so stack handling must be conservative. Symbolic execution must tolerate conditional control flow and unknown register origins without producing invalid memory access.
