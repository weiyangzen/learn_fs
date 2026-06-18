# sources/user-network-fs/samba/source4/lib/stream/packet.h

## Purpose

`packet.h` declares the framed packet stream API implemented by `packet.c`. It exposes an opaque `packet_context`, callback types, configuration setters, receive and send entry points, and standard frame-size detectors.

## Important APIs, Types, and Functions

Callback types are `packet_full_request_fn_t`, `packet_callback_fn_t`, `packet_send_callback_fn_t`, and `packet_error_handler_fn_t`. Public APIs include `packet_init()`, setter functions for callbacks/private/socket/event/fd/flags, `packet_recv()`, `packet_recv_disable()`, `packet_recv_enable()`, `packet_set_unreliable_select()`, `packet_send()`, `packet_send_callback()`, `packet_queue_run()`, `packet_full_request_nbt()`, and `packet_full_request_u32()`.

## Control Flow

The header itself has no runtime flow. Callers wire a context by setting socket, frame detector, receive callback, optional error handler, tevent fd/event context, then invoke `packet_recv()` from read readiness and `packet_queue_run()` from write readiness.

## State and Persistence Behavior

`packet_context` is opaque; callers manage it by talloc lifetime and setter functions. The API implies persistent buffering and queued-send state across readiness callbacks.

## Dependencies and Integration Points

The header forward-declares tevent and socket types and depends on Samba `NTSTATUS`, `DATA_BLOB`, and `TALLOC_CTX` through the includer. It bridges stream transports and socket backends.

## Risks and Edge Cases

The default error-handler ownership convention is not visible from the header, so callers may be surprised that private data can be freed. Callers must keep sent blob memory valid unless allowing `packet_send()` to steal it or enabling `nofree` with talloc-referenced data.

## Test Signals

Compile tests catch callback signature drift. Runtime tests should use custom frame detectors to validate callback ordering, error propagation, and queue behavior.
