# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevcgmx.h

Internal header for the CGM-writing library.

Key contents:
- Defines CGM binary opcode numbering with class/id shifts and the `cgm_op_index` enum.
- Defines the concrete `struct cgm_state_s`, including file handle, allocator, current metafile/picture/control/attribute state, aspect source flags, and command buffer.
- Sets `command_max_count` to 400 bytes and stores dynamic command state: `command_count`, `command_first`, and `result`.

Notable dependencies:
- Includes `gdevcgml.h`, making public CGM types available to the private implementation.

Research notes:
- This file is tightly paired with `gdevcgml.c`; external users should consume only `gdevcgml.h`.
- `command_max_count` must remain even because command writes pad to even byte counts.
