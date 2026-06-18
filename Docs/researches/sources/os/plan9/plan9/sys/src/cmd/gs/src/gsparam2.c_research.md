# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsparam2.c

Implements a stream-based serializer/deserializer for `gs_param_list`. The header file currently disables this interface behind `#if 0`, marking it as a future interface.

Key functions:
- `gs_param_list_puts`: serializes a read-mode list to a stream using variable-length words, key strings, type IDs, scalar bytes, arrays, string arrays, and recursive collections.
- `sput_word`, `sput_bytes`: write compressed integer and raw bytes to stream.
- `gs_param_list_gets`: deserializes from a stream into a write-mode list, allocating aggregate data as needed.
- `sget_word`, `sget_bytes`: read compressed integer and raw bytes from stream.

Integration:
- Includes `gsparams.h`, `stream` support indirectly, and parameter-list APIs.
- Intended replacement for the buffer serializer in `gsparams.c`.

Risk notes:
- Scalar serialization/deserialization uses intentional-looking fall-through from bool/int/long/float into null handling; this is fragile and comment-free.
- `gs_param_list_gets` indexes `gs_param_type_sizes[type]` before validating `type`.
- The `sget_bytes` function contains an apparent stray `};` before `return 0`, which would be a compile risk if this disabled future interface were enabled.
- String/name array deserialization allocates element strings but the visible code does not assign `sa->data` after reading each string, suggesting incomplete or stale implementation.
