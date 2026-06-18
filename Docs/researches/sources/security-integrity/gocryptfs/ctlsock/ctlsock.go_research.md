# sources/security-integrity/gocryptfs/ctlsock/ctlsock.go

Purpose: This package provides a Go client for gocryptfs control sockets.

Important APIs and functions: `CtlSock` wraps a Unix-domain socket connection. `New(socketPath)` connects with timeout behavior, `Query(req)` JSON-encodes a `RequestStruct`, reads and decodes a `ResponseStruct`, returns server-reported errors through `ResponseStruct.Error`, and `Close` closes the connection.

Control flow and state: A `CtlSock` instance owns one socket connection. Query is request/response over JSON and applies a 10-second timeout to avoid hangs.

Dependencies and integration points: Used by `gocryptfs-xray` and external tools to encrypt/decrypt paths through a mounted filesystem's control socket.

Risks and test signals: Risks include socket timeout tuning, JSON compatibility, and propagating server errors cleanly. Signals are round-trip path encrypt/decrypt queries and connection failure handling.
