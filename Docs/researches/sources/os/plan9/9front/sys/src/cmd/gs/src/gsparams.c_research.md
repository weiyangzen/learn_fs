# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsparams.c

Implements the active buffer-based serializer/expander for Ghostscript parameter lists.

Main behavior:
- `gs_param_list_serialize` walks a READ-mode parameter list, writes compressed key lengths, types, C-string keys, value headers, aligned aggregate data, and recursively serialized dictionaries.
- `gs_param_list_unserialize` expands the buffer into a WRITE-mode parameter list, reconstructing pointers into the serialized buffer where possible.
- Uses `WriteBuffer` to count required bytes even when the destination buffer is null or too small.
- Aligns aggregate payloads for element size or pointer-size requirements.

Important properties:
- The format is memory-layout-oriented and not portable across architectures with different type sizes/endianness/alignment.
- Designed so expanded values can point directly into the serialized input buffer.
