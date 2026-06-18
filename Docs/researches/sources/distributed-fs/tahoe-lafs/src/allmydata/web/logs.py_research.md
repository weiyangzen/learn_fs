# sources/distributed-fs/tahoe-lafs/src/allmydata/web/logs.py

## Purpose
Creates the authenticated private log-streaming WebSocket resource under `/private/logs/v1`. While a WebSocket is open, it forwards Eliot log messages as JSON frames.

## Important APIs, Types, And Functions
`TokenAuthenticatedWebSocketServerProtocol` subclasses Autobahn's Twisted `WebSocketServerProtocol` and implements `onConnect`, `_received_eliot_log`, `onOpen`, and `onClose`. `create_log_streaming_resource` builds a `WebSocketResource` with that protocol. `create_log_resources` builds a Twisted `Resource` with child `v1`.

## Control Flow
The private resource tree in `private.py` enforces the Tahoe auth-token HTTP scheme before this resource is reached. Once the WebSocket opens, `onOpen` registers `_received_eliot_log` as an Eliot destination. Every Eliot message is encoded with `json.dumps_bytes(..., any_bytes=True)` and sent as a WebSocket message. `onClose` removes the destination and tolerates `ValueError` if it was already removed.

## State And Persistence
There is no persisted state. Active state is one Eliot destination callback per open WebSocket connection. Log messages are transient and sent to clients as they arrive.

## Dependencies And Integration Points
The module depends on Autobahn Twisted WebSocket resources, Eliot, Twisted `Resource`, and Tahoe JSON bytes support. It is intentionally placed behind the authenticated private tree created in `private.py`. Test coverage is in `src/allmydata/test/web/test_logs.py`.

## Risks And Test Signals
The protocol class name mentions token authentication, but this module itself does not inspect headers; security depends on `/private` wrapping. `_received_eliot_log` has no send-error handling, so broken connections or serialization issues can affect destination cleanup. Test signals include successful child lookup at `/private/logs/v1`, WebSocket frame emission for Eliot messages, destination removal on close, and authentication tests in `test_private.py`.
