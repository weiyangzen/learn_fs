# sources/security-integrity/gocryptfs/gocryptfs-xray/paths_ctlsock.go

Purpose: This xray helper resolves encrypted/plain path translations through a running gocryptfs control socket.

Important APIs and functions: It opens a `ctlsock.CtlSock`, builds `RequestStruct` values for encrypt or decrypt path operations, sends queries, handles `ResponseStruct` errors, and prints or returns translated paths.

Control flow and state: Runtime state is the socket connection and request/response JSON. No filesystem state is changed except socket communication.

Dependencies and integration points: Connects `gocryptfs-xray` CLI modes with mounted gocryptfs instances that expose `-ctlsock`.

Risks and test signals: Requires a live matching mount and correct ABI. Signals are xray tests that map known plaintext/ciphertext names and graceful errors for missing sockets.
