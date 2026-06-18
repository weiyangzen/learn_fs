# sources/security-integrity/gocryptfs/internal/contentenc/content_test.go

Purpose: This test file validates content encryption offset/range logic, block splitting, encryption/decryption behavior, and merge semantics.

Important APIs and functions: Tests exercise range splitting helpers, `EncryptBlock`, `DecryptBlock`, `EncryptBlocks`, `DecryptBlocks`, `MergeBlocks`, block overhead/size conversions, and corrupted or special-case inputs.

Control flow and state: Tests create crypto cores/content encoders, encrypt plaintext blocks, decrypt them, compare output, and assert error behavior for tampering or malformed ciphertext.

Dependencies and integration points: Protects the core file data path used by mounted gocryptfs and fsck.

Risks and test signals: These tests are critical because block numbering and file ID AD must match between read and write. Signals include exact plaintext recovery, sparse zero-block behavior, wrong-block or wrong-file authentication failures, and range boundary correctness.
