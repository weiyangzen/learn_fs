# sources/distributed-fs/tahoe-lafs/src/allmydata/test/web/test_logs.py

## Purpose
This module tests Tahoe web log streaming resources, including the existence of the v1 HTTP resource and websocket streaming of Eliot log events.

## Important APIs, Types, And Functions
`StreamingEliotLogsTests` creates resources with `create_log_resources`, wraps them in a `RequestTraversalAgent`, and uses treq `HTTPClient`. `TestStreamingLogs` uses Autobahn's in-memory websocket agent and pumper with `TokenAuthenticatedWebSocketServerProtocol`. `has_response_code` asserts HTTP status. Eliot's `log_call` creates test actions.

## Control Flow
The HTTP test requests `http:///v1` and expects `OK`. The websocket test opens `ws://localhost:1234/ws`, registers a message callback, executes an Eliot-decorated function with mixed unicode, bytes, numbers, dicts, and lists, then closes the transport and asserts three streamed messages with expected action type, JSON-safe argument representation, and started/succeeded action statuses.

## State And Persistence
All state is in memory: memory reactor, websocket pumper, captured message list, and transient Eliot log events. There is no filesystem persistence.

## Dependencies And Integration Points
The module integrates Tahoe log resources with treq testing agents, Autobahn Twisted websocket testing, Eliot action logging, JSON encoding, Twisted memory reactor, and Async/Sync Tahoe test cases.

## Risks And Test Signals
Signals include route existence, websocket protocol wiring, Eliot event subscription, JSON serialization of non-UTF-8 bytes, and lifecycle message delivery. Risks include timing/pumper lifecycle sensitivity and narrow authentication coverage despite use of a token-authenticated protocol class.
