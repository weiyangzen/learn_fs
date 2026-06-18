# sources/sync-backup/syncthing/cmd/strelaysrv/testutil/main.go

Purpose: manual command-line utility for testing relay join/connect/test flows against a relay server.

Important APIs/functions: `main`, `stdinReader`, and `connectToStdio`.

Control flow: loads a TLS keypair, derives the device ID, parses relay URL, reads stdin asynchronously, and runs one of three modes. `-join` creates a relay client, serves it, receives session invitations, joins sessions, and bridges to stdio. `-connect` requests an invitation for a target device and joins it. `-test` uses `client.TestRelay`.

State and persistence: uses certificate/key files for identity; otherwise no persistence. Runtime state is relay client connection/invitation channels.

Dependencies/integration: depends on relay client and relay protocol packages. It is intended to exercise `strelaysrv` behavior externally.

Risks and test signals: useful for interactive/manual verification, but not automated. `connectToStdio` polls reads with millisecond deadlines and writes stdin lines, which is simple but not throughput-oriented.
