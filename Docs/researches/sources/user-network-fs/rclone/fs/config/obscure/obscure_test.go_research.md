<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/obscure/obscure_test.go -->
# sources/user-network-fs/rclone/fs/config/obscure/obscure_test.go

## Purpose
Verifies the obscuring codec with deterministic IVs and malformed input cases.

## Important APIs, Types, And Control Flow
Tests temporarily replace package `cryptRand` with fixed byte buffers, assert exact `Obscure` output for empty and non-empty strings, round-trip through `Reveal`, and exercise `MustObscure`/`MustReveal`. Error cases cover illegal base64 and ciphertext shorter than the AES block IV.

## State And Persistence
The only mutated state is package-level `cryptRand`, restored to `rand.Reader` after deterministic calls. No filesystem persistence is used.

## Dependencies And Integration Points
Uses `bytes.Buffer`, `crypto/rand`, and testify. It directly tests unexported package state because it is in package `obscure`.

## Risks And Test Signals
Good signal for format stability and failure messages. It does not test random-reader failure or oversized values, both handled in production code.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/obscure/obscure_test.go -->
