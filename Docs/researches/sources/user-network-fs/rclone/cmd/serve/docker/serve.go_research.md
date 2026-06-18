# sources/user-network-fs/rclone/cmd/serve/docker/serve.go

## Purpose

`serve.go` provides the HTTP server wrapper for Docker plugin communication over Unix sockets, systemd-activated sockets, or TCP.

## Important APIs, Types, and Functions

`type Server http.Server`, `NewServer`, `Shutdown`, `serve`, `ServeUnix`, `ServeTCP`, and `writeSpecFile` are the main APIs.

## Control Flow

`ServeUnix` obtains a Unix listener, logs whether it is self-created or systemd-provided, and serves. `ServeTCP` binds TCP, optionally wraps TLS, writes a Docker spec file unless disabled, and serves. `serve` registers cleanup for temp files and delegates to `http.Server.Serve`.

## State and Persistence Behavior

The server writes a Docker spec file for TCP mode and registers atexit removal for spec files or self-created sockets. It does not persist volume state directly.

## Dependencies and Integration Points

It depends on platform `newUnixListener`, Docker plugin spec-file discovery, TLS, rclone file helpers, and atexit cleanup.

## Risks and Test Signals

Risks include stale spec/socket cleanup only on normal atexit, TLS protocol assumptions, Docker discovery path permissions, and use of temp dir for Windows default spec dir. API tests exercise server startup/shutdown in TCP and Unix modes where enabled.
