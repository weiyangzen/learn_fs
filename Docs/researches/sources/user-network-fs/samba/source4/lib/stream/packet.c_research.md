# sources/user-network-fs/samba/source4/lib/stream/packet.c

## Purpose

`packet.c` implements a helper layer that turns a byte stream socket into framed request callbacks and queued packet sends. It handles partial reads, multiple frames in one read, event-boundary scheduling, serialized callbacks, temporary receive disablement, and write queue callbacks.

## Important APIs, Types, and Functions

The central type is private `struct packet_context`. Exported setup functions include `packet_init()`, callback/error/private setters, socket/event/fd setters, `packet_set_serialise()`, `packet_set_initial_read()`, `packet_set_nofree()`, and `packet_set_unreliable_select()`. Runtime APIs are `packet_recv()`, `packet_recv_disable()`, `packet_recv_enable()`, `packet_queue_run()`, `packet_send_callback()`, `packet_send()`, and full-request helpers `packet_full_request_nbt()` and `packet_full_request_u32()`.

## Control Flow

`packet_recv()` is called when the fd is readable. It guards against reentrant processing, honors receive disablement, computes bytes to read from known packet size, initial-read hint, or `socket_pending()`, expands the partial buffer, reads through `socket_recv()`, and asks `full_request()` whether a complete frame is present. Complete frames are passed to `callback()`. Extra buffered frames are either processed immediately or scheduled on a zero-time tevent timer to preserve event boundaries. `packet_queue_run()` drains queued sends until the socket would block or the queue empties.

## State and Persistence Behavior

The packet context persists partial input bytes, current packet size, send queue elements, callback pointers, and flags. Its destructor refuses to free while callbacks are busy and defers actual free until processing unwinds. Send blobs are either stolen into queue elements or referenced when `nofree` is set.

## Dependencies and Integration Points

It depends on dlinklist helpers, tevent fd/timer APIs, `socket_context`, `DATA_BLOB`, and SMB length helpers from `libcli/raw/smb.h`. It is used by higher-level stream protocols that need framed messages over source4 sockets.

## Risks and Edge Cases

Correctness depends on `full_request()` returning consistent sizes. The code contains explicit overflow and pointer-wrap checks, but a buggy callback can still report invalid packet sizes. Default error handling frees `private_data`, which is a strong ownership convention. `unreliable_select` loops can read buffered TLS data without fd readiness but must avoid spinning.

## Test Signals

Useful tests should cover NBT and u32 framing, multiple frames in one read, partial frames, callback errors, send callbacks, `nofree` ownership, serialized reentrancy, receive disable/enable, and TLS-like unreliable select behavior.
