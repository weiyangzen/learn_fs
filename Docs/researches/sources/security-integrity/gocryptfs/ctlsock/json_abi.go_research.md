# sources/security-integrity/gocryptfs/ctlsock/json_abi.go

Purpose: This file defines the stable JSON request/response ABI for the gocryptfs control socket.

Important APIs and types: `RequestStruct` carries either encryption or decryption path requests and must not request both at once. `ResponseStruct` carries encrypted/decrypted paths and an error string.

Control flow and state: No executable logic except methods in companion files; the struct field names and JSON encoding form the wire contract.

Dependencies and integration points: Shared by the client package, control socket server, and `gocryptfs-xray`.

Risks and test signals: ABI changes can break external tools. Signals include JSON round-trip tests and compatibility with older mounted gocryptfs instances.
