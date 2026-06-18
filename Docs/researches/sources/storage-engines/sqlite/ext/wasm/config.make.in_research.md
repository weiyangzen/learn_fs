# sources/storage-engines/sqlite/ext/wasm/config.make.in

## Purpose

`config.make.in` is a tiny configure-generated Makefile fragment for the SQLite WASM extension build. The top-level configure script substitutes tool paths into this template to produce `config.make`.

## Important APIs, Types, and Functions

This is make configuration rather than executable code. It defines:

- `bin.bash = @BIN_BASH@`
- `bin.emcc = @EMCC_WRAPPER@`
- `bin.wasm-strip = @BIN_WASM_STRIP@`
- `bin.wasm-opt = @BIN_WASM_OPT@`
- `SHELL = $(bin.bash)`

The commented-out override block is a local testing aid for Makefile validation and conditional branches.

## Control Flow

The configure phase replaces `@...@` tokens with discovered or configured executable paths. The generated `config.make` is then included by WASM build makefiles so they can invoke Bash, Emscripten, wasm-strip, and wasm-opt consistently.

## State and Persistence

The file itself has no runtime state. The generated `config.make` persists build configuration choices for a checkout or build directory until configure is rerun.

## Dependencies and Integration Points

It integrates the top-level SQLite configure script with the `ext/wasm` Makefile layer. It assumes configure has resolved the Bash path, an Emscripten compiler wrapper, and optional WebAssembly optimization/stripping tools.

## Risks and Edge Cases

- Empty substitutions can lead to later build failures unless downstream make logic validates them.
- `SHELL` is explicitly bound to `$(bin.bash)`, so an incorrect Bash path affects all shell command execution in included makefiles.
- The commented testing overrides can be useful locally but would break real builds if uncommented and committed.

## Test Signals

Build tests should verify that configure generates non-empty paths for required tools in normal WASM builds, that optional tool absence is handled by downstream logic, and that make targets fail clearly when `bin.bash` or `bin.emcc` is invalid.
