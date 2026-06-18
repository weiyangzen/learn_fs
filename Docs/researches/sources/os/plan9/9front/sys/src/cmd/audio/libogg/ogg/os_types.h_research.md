# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libogg/ogg/os_types.h

## Role

This small header provides libogg platform type aliases and allocator macros for the 9front vendored build.

## Definitions

It maps allocator hooks directly to libc:

- `_ogg_malloc` -> `malloc`
- `_ogg_calloc` -> `calloc`
- `_ogg_realloc` -> `realloc`
- `_ogg_free` -> `free`

It defines fixed-width-style integer names used by libogg:

- `ogg_int16_t`, `ogg_uint16_t`
- `ogg_int32_t`, `ogg_uint32_t`
- `ogg_int64_t`

## Integration Notes

The header assumes the included environment already provides declarations for the allocator functions through surrounding includes. It is included by `ogg.h`, which then exposes these types to libogg users.
