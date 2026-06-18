# File Research: sources/os/bsd/freebsd-src/sys/kern/firmw.S

## Summary
Assembly helper for embedding a firmware binary into a kernel object.

## Main Contents
- Defines `FIRMW_START(S)` and `FIRMW_END(S)` symbol macros.
- Places contents of `FIRMW_FILE` into `.rodata` using `.incbin`.
- Exports `_binary_<symbol>_start` and `_binary_<symbol>_end`-style object symbols.
- Emits an AArch64 GNU property note when building for `__aarch64__`.

## Important Behavior
The build system supplies `FIRMW_SYMBOL` and `FIRMW_FILE`. The resulting object exposes firmware start/end addresses for C code to consume.

## Risks
Incorrect macro definitions or file paths would create missing or misnamed firmware symbols. The data is read-only and has no runtime logic beyond symbol layout.
