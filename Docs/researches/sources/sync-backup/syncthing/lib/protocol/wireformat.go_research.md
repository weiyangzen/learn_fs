# sources/sync-backup/syncthing/lib/protocol/wireformat.go

## Purpose
Connection wrapper that converts high-level protocol structs into wire-format naming before they enter encryption/raw connection layers. It ensures outgoing index, index update, and request messages use canonical wire representation.

## Important APIs, Types, and Functions
`wireFormatConnection` embeds `Connection`. It overrides `Index`, `IndexUpdate`, and `Request` to call `idx.toWireFormat()`, `idxUp.toWireFormat()`, and `req.toWireFormat()` before delegating. Other connection methods come from the embedded connection.

## Control Flow
Each overridden method mutates the provided message into wire format, then calls the same method on the wrapped connection. `Request` returns the wrapped connection's response bytes and error unchanged.

## State and Persistence Behavior
No state is stored. The wrapper intentionally mutates caller-provided message structs, matching `Connection` interface documentation that messages may be altered and should not be reused.

## Dependencies and Integration Points
Used as the outer connection returned by `NewConnection`, after encryption has been layered over raw connection. It integrates with file-info and request conversion helpers defined elsewhere in the protocol package.

## Risks and Edge Cases
Because conversion is in-place, callers that reuse message values after sending can observe canonicalized names or metadata. The wrapper only covers outgoing `Index`, `IndexUpdate`, and `Request`; adding new message types with path fields requires corresponding wrapper updates.

## Test Signals
`protocol_test.go` unwrapping helpers account for this wrapper, and connection tests exercise it indirectly through `NewConnection`. Direct tests would assert message mutation into canonical wire form.
