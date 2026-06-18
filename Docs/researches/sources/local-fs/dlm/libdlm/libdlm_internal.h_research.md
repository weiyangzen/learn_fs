# File Research: sources/local-fs/dlm/libdlm/libdlm_internal.h

## Purpose
Internal compatibility header for building libdlm with kernel-style DLM headers.

## Contents
- Defines `__user`.
- Typedefs `__u8`, `__u16`, and `__u32`.
- Defines `BUILDING_LIBDLM`.

## Notes
- This avoids depending on kernel annotation/type definitions in contexts where only user-space fixed-width integer types are available.
