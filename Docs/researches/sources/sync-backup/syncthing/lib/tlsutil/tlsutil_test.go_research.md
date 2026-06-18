# sources/sync-backup/syncthing/lib/tlsutil/tlsutil_test.go

Purpose: tests connection first-byte preservation/TLS detection and TLS 1.2 cipher-suite set.

Important tests: `TestUnionedConnection` feeds fake accepted connections with first byte `0x16` and non-`0x16` data, checks `AcceptNoWrapTLS` classification, and reads all bytes back to ensure the initial byte is not lost and the first read returns exactly one byte. `TestCheckCipherSuites` verifies `SecureDefaultWithTLS12` returns exactly the expected cipher IDs with no duplicates or unknown suites.

State and persistence: fake in-memory listener and connection only.

Dependencies and integration: validates exported listener/helper behavior without network sockets.

Risks and signals: no tests for `Accept` TLS wrapping, certificate generation/writing, read-deadline errors, or empty first reads.
