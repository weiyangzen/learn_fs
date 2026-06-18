# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsdsrc.h

This header defines the generic `gs_data_source_t` abstraction used by constructs that can read from strings, byte objects, float arrays, or positionable streams.

Key pieces:
- `data_source_proc_access` callback signature.
- `gs_data_source_type_t` enum for string, bytes, floats, and stream.
- `gs_data_source_s` storing an access function, type, and either `gs_const_string` or `stream *`.
- Macros for direct access or copy-only access that propagate negative errors.
- Initialization macros for strings, raw bytes, float arrays, and streams.
- GC descriptor declaration `st_data_source`.

Important notes from comments:
- Clients supply buffers.
- Access may return a direct pointer or copy into the buffer.
- Bounds checking is implementation-dependent except for streams.
- Float-array handling is described as anomalous but retained for lack of a better abstraction.
