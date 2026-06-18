# File Research: sources/windows/winfsp/src/dll/fuse3/fuse3_compat.c

This file exports plain `fuse3_*` compatibility symbols.

Key responsibilities:
- Includes `dll/library.h`.
- Redefines `FSP_FUSE_API` and `FSP_FUSE_SYM` so included FUSE3 headers emit exported forwarding implementations.
- The comment states these symbols are for FFI consumers such as fusepy or jnr-fuse, not normal C/C++ code; headers expose `fsp_fuse3_*` wrapped by macros for C/C++ consumers.

Filesystem relevance:
- ABI compatibility shim for external FFI callers.
- Runtime behavior is delegated to the default `fsp_fuse_env` and the `fsp_fuse3_*` implementation.
