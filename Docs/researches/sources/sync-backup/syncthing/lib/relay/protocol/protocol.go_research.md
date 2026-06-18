# sources/sync-backup/syncthing/lib/relay/protocol/protocol.go

## Purpose
Implements relay protocol message framing over an `io.Reader`/`io.Writer`: write a magic/type/length XDR header plus payload, and read/validate headers before unmarshalling typed packet payloads.

## Important APIs, Types, and Functions
Constants include `magic` and `ProtocolName`. Response variables include success, not found, already connected, wrong token, and unexpected message. Public functions are `WriteMessage` and `ReadMessage`.

## Control Flow
`WriteMessage` switches on the concrete packet type, marshals it with XDR, sets the header message type and length, marshals the header, and writes header plus payload. `ReadMessage` reads a fixed-size header, validates magic and length range, reads payload, switches on message type, unmarshals into the corresponding packet struct, and returns an error for unknown types. A zero-length `JoinRelayRequest` is accepted for backward compatibility with older no-token protocol versions.

## State and Persistence Behavior
No state is kept. The functions perform synchronous I/O on supplied streams and allocate payload buffers sized by the header length.

## Dependencies and Integration Points
Depends on generated XDR packet methods and is used by relay clients and servers for ping/pong, join, connect, invitation, response, and relay-full messages. `ProtocolName` is used in TLS ALPN negotiation.

## Risks and Edge Cases
`ReadMessage` limits payloads to 1024 bytes, which protects memory but must remain large enough for valid packets. Unknown message types and magic mismatches are hard errors. `WriteMessage` uses `append(headerpayload, payload...)`, which is simple but allocates a combined slice. Backward compatibility for zero-length join requests is intentional.

## Test Signals
The package has only an empty test file in this subset. Useful tests would cover all packet round trips, bad magic, negative/oversized lengths, unknown types, and legacy zero-length join relay requests.
