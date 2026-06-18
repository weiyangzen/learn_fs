# sources/storage-engines/sqlite/tool/emcc.sh.in

## Purpose
`emcc.sh.in` is a configure-time template for a shell wrapper around Emscripten's `emcc`. It locates `emcc` directly or via an EMSDK installation and then execs the compiler with the caller's arguments.

## Important APIs, Types, and Functions
Template variables `@EMSDK_HOME@`, `@EMSDK_ENV_SH@`, and `@BIN_EMCC@` are substituted by configure. The script uses `which emcc`, environment variable checks, optional sourcing of `emsdk_env.sh`, and `exec $emcc "$@"`.

## Control Flow
The generated script first uses configured `emcc`, then PATH. If not found, it requires `EMSDK_HOME`, determines `EMSDK_ENV_SH`, validates that file, sources it quietly if `$EMSDK` is not already set, looks for `emcc` again, and exits with distinct error codes for missing configuration or compiler. On success it replaces itself with `emcc`.

## State and Persistence
It does not persist files. It mutates the current shell process environment only until `exec`, primarily through sourced EMSDK variables.

## Dependencies and Integration Points
It depends on Bourne-like shell behavior, though it uses `source`, which is not strictly POSIX `sh`. It integrates with SQLite's configure output and WebAssembly/Emscripten build path.

## Risks
The `source` keyword can fail under shells that only support `.`. `exec $emcc "$@"` leaves `$emcc` unquoted, so paths containing spaces are unsafe. The wrapper trusts configure substitutions and the EMSDK environment script. Error codes are meaningful but only if callers preserve them.

## Test Signals
Test configured `@BIN_EMCC@`, PATH-only `emcc`, EMSDK discovery with and without pre-set `$EMSDK`, missing `EMSDK_HOME`, missing `emsdk_env.sh`, and compiler paths containing spaces.
