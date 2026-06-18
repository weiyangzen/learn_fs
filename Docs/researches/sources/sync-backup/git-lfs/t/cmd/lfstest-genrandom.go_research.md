# sources/sync-backup/git-lfs/t/cmd/lfstest-genrandom.go

Purpose: emits cryptographically random bytes for integration tests, optionally base64/base64url encoded.

Important behavior: parses `--base64` or `--base64url`, optional byte count, defaults to maximum `uint64`, reads 32-byte chunks from `crypto/rand`, encodes if requested, and writes exactly up to the requested count.

Control flow: validates at most one size arg after option, loops while `count > 0`, handles read/write errors with distinct exit codes.

State/persistence behavior: writes random data to stdout only.

Dependencies/integration: used by shell tests needing arbitrary object data.

Risks: default unbounded output can run indefinitely if no size is supplied. Encoded output count is in output bytes, not raw bytes.

Test signals: exit status, output length, and encoding alphabet.
