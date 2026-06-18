# sources/user-network-fs/rclone/lib/random/random.go

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/random/random.go -->
## sources/user-network-fs/rclone/lib/random/random.go

Purpose: provides random strings for tests/user-friendly names and cryptographically strong URL-safe passwords.

Important APIs and control flow: `StringFn(n, randReader)` fills `n` bytes from a supplied reader and maps each byte into a repeating consonant/vowel/consonant/vowel/consonant/vowel/consonant/digit pattern. `String(n)` uses `crypto/rand.Reader`. `Password(bits)` rounds requested bits up to bytes, reads that many bytes from `crypto/rand`, verifies a full read, and returns raw URL-safe base64 without padding.

State, dependencies, and integration: functions are stateless. Dependencies include `crypto/rand`, `encoding/base64`, and `io`. `StringFn` accepts injected readers for deterministic/failure testing but panics on read failure because it is intended for non-password utility/test use.

Risks and test signals: `String` is explicitly not for passwords and its modulo mapping is biased. `Password` length is bit-count rounded up, so entropy is at least requested bits but output length follows base64 expansion. Tests cover output lengths and duplicate smoke checks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/random/random.go -->
