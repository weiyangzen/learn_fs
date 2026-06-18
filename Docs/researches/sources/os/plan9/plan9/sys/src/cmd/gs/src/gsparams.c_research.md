# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsparams.c

Implements the active buffer-based serializer and expander for parameter lists.

Key functions:
- `gs_param_list_serialize`: writes a parameter list into an aligned byte buffer, returning the required size even when the buffer is null or too small.
- `gs_param_list_unserialize`: expands a buffer back into a write-mode parameter list.
- `ptr_align_to`, `wb_put_alignment`: alignment helpers for direct buffer references.
- `wb_put_word`, `buf_get_word`: variable-length integer encoding/decoding.
- `wb_put_bytes`: size-counting and bounded copy helper.

Serialization model:
- Each entry stores compressed key length, type, null-terminated key, then type-specific payload.
- Scalar and homogeneous structs are stored as memory images.
- Aggregate payloads are aligned so the unserialized list can point into the source buffer.
- Dictionaries recurse and write an end marker.

Integration:
- Public interface declared in `gsparams.h`.
- Used where compact in-memory parameter-list transport is required.

Risk notes:
- This format is architecture-sensitive because it stores unpacked C memory images for numeric/scalar structures.
- `gs_param_list_unserialize` trusts source buffer structure and type IDs; malformed buffers can walk memory.
- String array unserialization mutates string descriptors in the input buffer by assigning `sa->data` and `persistent`.
