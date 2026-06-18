# sources/security-integrity/gocryptfs/tests/reverse/ctlsock_test.go

## Purpose
Verifies reverse-mode control socket `EncryptPath` and `DecryptPath` operations against a deterministic fixture tree with short and long names.

## Important APIs, Types, And Functions
- `ctlSockTestCases` maps encrypted fixture paths to plaintext paths.
- `TestCtlSockPathOps` round-trips every case through `ctlsock.RequestStruct`.
- `TestCtlSockCrash` sends a malformed longname request under relaxed panic/syslog settings.

## Control Flow
The tests mount `ctlsock_reverse_test_fs` in reverse mode with a per-test socket, then issue decrypt and encrypt requests. After populating longname parent caches, they query deliberately wrong parent/name combinations and expect `ENOENT`.

## State And Persistence
State is the mounted fixture tree and its control socket. The fixture config and files provide deterministic encrypted names.

## Dependencies And Integration Points
Depends on `ctlsock`, `test_helpers.QueryCtlSock`, `test_helpers.MountOrFatal`, and reverse package `plaintextnames` to skip non-encrypted-name modes.

## Risks And Edge Cases
Hard-coded names are brittle by design; any encryption, longname, or fixture config change requires updating the table. Crash coverage intentionally does not assert much beyond not terminating the mount.

## Test Signals
Pass signals are exact path round trips, expected `ENOENT` for cache mixups, and no panic/crash on nonsensical longname input.
