# sources/distributed-fs/tahoe-lafs/ws_client.py

## Purpose
This script is a Twisted/Autobahn WebSocket client for streaming Tahoe-LAFS private log messages from a local testgrid node.

## Important APIs, Types, and Functions
`TahoeLogProtocol` subclasses `WebSocketClientProtocol` and implements `onOpen`, `onMessage`, and `onClose`. `main(reactor)` reads Tahoe config, extracts `api_auth_token` and `node.web.port`, builds a `WebSocketClientFactory` for `/private/logs/v1`, and connects through `HostnameEndpoint`. The script runs with `twisted.internet.task.react`.

## Control Flow
`main` starts Twisted logging, assumes `tahoe_dir = "testgrid/alice"`, reads private and public node config, normalizes `tcp:` ports, creates deferreds `factory.on_open` and `factory.on_close`, connects to localhost, waits for open, then waits for close. `onOpen` callbacks `on_open`; `onMessage` prints raw payload bytes and flushes stdout; `onClose` errbacks open if the connection closed before opening, then callbacks `on_close`.

## State and Persistence
The script reads existing Tahoe node config and private API token. It persists nothing, but emits log payloads to stdout and Twisted connection diagnostics to stdout.

## Dependencies and Integration Points
Depends on Twisted endpoints/deferreds/reactor, Autobahn WebSocket client classes, and `allmydata.client.read_config`. It integrates with Tahoe's private logs WebSocket endpoint and token-based authorization header format `tahoe-lafs <token>`.

## Risks and Test Signals
The hard-coded `testgrid/alice` path makes this a developer utility rather than generic CLI. `onClose` always callbacks `on_close`; repeated close/error edge cases depend on Deferred state. The disabled JSON pretty-print branch suggests expected Eliot JSON payloads but current behavior prints bytes. Tests should cover port parsing, Authorization header construction, failed connect handling, and protocol deferred sequencing.
