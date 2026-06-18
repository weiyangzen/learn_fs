# sources/distributed-fs/tahoe-lafs/integration/test_streaming_logs.py

## Purpose
Tests the private WebSocket streaming log endpoint by authenticating with Alice's API token, provoking a log event, and requiring a JSON message before connection close.

## Important APIs, Types, and Functions
`_url_to_endpoint` maps a WebSocket URL to `HostnameEndpoint`. `_StreamingLogClientProtocol` reports open, first message, and close through Deferreds. `_connect_client` builds an Autobahn `WebSocketClientFactory` with `Authorization: <SCHEME> <api_auth_token>`. `_race` returns a `Left` or `Right` wrapper for whichever Deferred fires first and cancels the loser.

## Control Flow
`_test_streaming_logs` reads Alice's `node.url` and private `api_auth_token`, converts HTTP URL to WS URL, connects to `private/logs/v1`, prepares close/message Deferreds, makes a normal HTTP GET with `treq` to generate a log event, then asserts the race resolves to `Right` and the payload parses as JSON.

## State and Persistence
Reads node config/private config but does not modify persistent Tahoe state. The only state is live WebSocket connection state and transient log events.

## Dependencies and Integration Points
Depends on Autobahn WebSocket client, Twisted endpoint connection, Tahoe private web API auth scheme, `treq`, and Alice's web node configuration.

## Risks
Race logic is sensitive to connection close timing. The test validates only that some first payload is JSON, not schema content. It uses private API token material and will fail if auth scheme formatting changes.

## Test Signals
The key signal is receiving a JSON log payload before the WebSocket closes after a web request provokes logging.
