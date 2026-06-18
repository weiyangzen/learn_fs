# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsdsrc.c

This file implements `gs_data_source_t` access and GC tracing.

GC behavior:
- Strings trace as const strings.
- Streams trace as stream pointers.
- Byte and float arrays trace through `data.str.data`.

Accessors:
- `data_source_access_string` returns or copies a pointer into a const string without bounds checks.
- `data_source_access_bytes` is identical at runtime but uses byte/floats GC semantics.
- `data_source_access_stream` supports buffered direct access when the requested range is already in the stream buffer; otherwise it seeks and reads, returning `gs_error_rangecheck` on seek/read/short-read failure.

The distinction between string and bytes access is mainly for garbage collection, not for data movement.
