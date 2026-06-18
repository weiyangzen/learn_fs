# sources/object-store/garage/src/net/error.rs

## Purpose
This file defines the error type and logging helpers for `garage_net`, plus compact serialization helpers for I/O error kinds in stream error frames.

## Important APIs, types, and functions
`Error` includes I/O, messagepack encode/decode, Tokio join, oneshot receive, handshake, UTF-8, framing, remote I/O error, request ID collision, message, no-handler/shutdown, connection closed, and version mismatch variants. `From` implementations map watch/mpsc send errors into messages. `LogError` logs and discards nested result errors. `u8_to_io_errorkind` and `io_errorkind_to_u8` map selected `io::ErrorKind` values to stable small integers.

## Control flow
Send/recv loops and connection setup use `?` to propagate `Error`. Error frames encode `io::ErrorKind` with `io_errorkind_to_u8`; receivers reconstruct remote errors using `u8_to_io_errorkind`.

## State and persistence behavior
No persistent state. Error kind numeric codes are part of the wire protocol for stream error frames.

## Dependencies and integration points
It depends on `thiserror`, `log`, `rmp-serde`, `tokio`, and `kuska-handshake`. All net modules import this error type.

## Risks and edge cases
Unknown error kinds collapse to `Other`. MPSC/watch send errors lose detail. `Remote` carries kind and string but not structured application error types. Changing numeric mappings would affect compatibility with older peers.

## Test signals
No direct tests. Useful tests should cover error kind round-trips, remote error frame decoding, `LogError` behavior, and version/no-handler mapping in endpoint calls.
