# sources/security-integrity/gocryptfs/internal/configfile/scrypt_test.go

Purpose: This test file validates scrypt KDF construction, parameter bounds, and derived-key behavior.

Important APIs and functions: Tests cover `NewScryptKDF`, `DeriveKey`, default logN behavior, invalid cost handling, salt presence, and output length or consistency expectations.

Control flow and state: Tests create KDF objects and derive keys from test passwords. No persistent repository files are modified.

Dependencies and integration points: Protects password-to-key derivation used by config encryption/decryption.

Risks and test signals: KDF tests can be time-sensitive if they run expensive settings. Signals include deterministic derivation for same salt/password, different salts producing different keys, and validation of allowed logN range.
