# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevcgmx.h

Internal header for the CGM-writing library.

Key contents:
- Defines packed internal CGM opcode indices grouped by CGM class.
- Defines shifts used to encode command class and element id.
- Defines `struct cgm_state_s`, including output file, allocator, current metafile/picture/control/attribute state, aspect source flags, command buffer, command count, continuation state, and last result.
- Sets `command_max_count` to 400 bytes and requires it to be even.

Important behavior:
- The opcode enum is the internal bridge between symbolic API calls and CGM binary command headers.
- `cgm_state_s` stores both durable CGM settings and transient command serialization state.
- Some state areas are placeholders or comments, such as text alignment, pattern table, and color table.

Dependencies:
- Includes `gdevcgml.h` for public CGM types.

Notable risks:
- The state struct stores many fields that may be uninitialized unless the relevant API call was made.
- `source_flags` is hard-coded to 18 entries, matching the current aspect source enum count.
- Command serialization depends on enum values and bit shifts remaining consistent with CGM binary encoding.
