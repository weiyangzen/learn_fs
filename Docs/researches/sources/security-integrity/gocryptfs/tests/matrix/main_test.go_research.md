# sources/security-integrity/gocryptfs/tests/matrix/main_test.go

## Purpose
Defines the matrix test harness for gocryptfs forward-mode integration tests. It reruns the same package tests across combinations of filename encryption, OpenSSL acceleration, AES-SIV, raw64, XChaCha, serialized reads, shared storage, and deterministic names.

## Important APIs, Types, And Functions
- `testcaseMatrix` records the active mode: `plaintextnames`, `openssl`, `aessiv`, `raw64`, and `extraArgs`.
- `testcase` and `ctlsockPath` are package globals consumed by other matrix tests.
- `(*testcaseMatrix).isSet` checks whether a mount option is active.
- `TestMain` is the package entry point and loops over every configured matrix row.

## Control Flow
`TestMain` parses flags, skips OpenSSL-only rows when built without OpenSSL, resets the shared temp directories, builds mount arguments, mounts gocryptfs with `-zerokey` and a control socket, runs `m.Run`, checks the test process for file descriptor leaks, unmounts, and exits on the first failing matrix row.

## State And Persistence
The harness recreates `test_helpers.DefaultPlainDir` and `DefaultCipherDir` for every row, optionally writes `gocryptfs.diriv`, creates a per-row control socket, and removes it after unmount to avoid asynchronous socket cleanup races.

## Dependencies And Integration Points
Depends on `internal/stupidgcm` for OpenSSL build detection and on `tests/test_helpers` for reset, mount, fd listing, and unmount behavior. All package tests implicitly depend on the global `testcase` and default directories initialized here.

## Risks And Edge Cases
Because the same tests run many times, leaked file descriptors or stale mount state can cascade. Mode flags alter expected behavior, especially reserved names, diriv files, and deterministic name handling.

## Test Signals
Signals success by completing every matrix row with `m.Run()==0`, stable fd counts, and clean unmounts. Failures identify the exact matrix row printed by `TestMain`.
