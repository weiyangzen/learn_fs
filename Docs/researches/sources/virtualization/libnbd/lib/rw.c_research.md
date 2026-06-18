# File Research: sources/virtualization/libnbd/lib/rw.c

Implements synchronous and asynchronous NBD commands for reads, writes, flush, trim, cache, zero, and block status.

Synchronous flow:
- Each synchronous API calls the async version with a null completion callback, then waits with `wait_for_command`.
- Structured read and block-status sync APIs assert callback ownership was transferred.

Core async queueing:
- `nbd_internal_command_common`: rejects commands after disconnect, checks in-flight overflow, applies strict zero-size/bounds/alignment validation, enforces request/payload limits, allocates command, assigns cookie, copies callbacks, initializes read-safety flag, appends to queue, and kicks generated state machine if ready.
- Commands move through `cmds_to_issue`, `cmds_in_flight`, and `cmds_done`.

Feature validation:
- Read structured validates DF support in strict mode.
- Write auto-manages `PAYLOAD_LEN` with extended headers when strict auto flag is enabled and checks readonly/FUA.
- Flush, trim, cache, zero check negotiated server capabilities in strict command mode.
- Block status requires structured replies and negotiated metadata contexts.
- Filtered block status requires extended headers and block-status payload support, then converts requested context names to negotiated context IDs.

Interactions:
- Uses feature queries from `flags.c`.
- Uses protocol command constants from `nbd-protocol.h`.
- Generated state machine consumes queued commands.

Research notes:
- Read buffers default to pre-initialized safety behavior through `h->pread_initialize`.
- Filtered block-status payload stores length high/low words followed by context IDs in network order.
- The command-common error cleanup path for block-status callbacks appears inconsistent with the normal retire path: it frees `extent32` when `wide` is true and `extent64` when false, while `aio.c` does the opposite.
