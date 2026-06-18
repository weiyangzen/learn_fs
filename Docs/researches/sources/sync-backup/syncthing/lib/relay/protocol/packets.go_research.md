# sources/sync-backup/syncthing/lib/relay/protocol/packets.go

## Purpose
Defines relay protocol packet types, message type constants, the wire header shape, common response values, and string formatting for session invitations.

## Important APIs, Types, and Functions
Constants enumerate message types for ping, pong, join relay, join session, response, connect request, session invitation, and relay full. Types are `header`, empty packets `Ping`, `Pong`, `RelayFull`, `JoinRelayRequest`, `JoinSessionRequest`, `Response`, `ConnectRequest`, and `SessionInvitation`. `SessionInvitation.String` and `GoString` format inviter device ID plus IP and port.

## Control Flow
Packet definitions are passive. `SessionInvitation.String` attempts to parse `From` as a Syncthing device ID, falls back to `<invalid>`, and formats address bytes as `net.IP` with port.

## State and Persistence Behavior
No state or persistence. Packet values are serialized by generated XDR methods and `protocol.go` read/write helpers.

## Dependencies and Integration Points
Depends on `net`, `fmt`, and Syncthing `protocol.DeviceIDFromBytes`. The `go:generate` directive generates `packets_xdr.go`; relay client/server code depends on these structures for handshake and session setup.

## Risks and Edge Cases
The max-size comments in struct fields are enforced by generated XDR marshal/unmarshal code, not by constructors. Message type order is part of the wire protocol and must remain compatible. `SessionInvitation.String` can display invalid device IDs if packet data is malformed.

## Test Signals
No direct tests here. Compile plus XDR generation consistency and client/server interoperability are the main signals.
