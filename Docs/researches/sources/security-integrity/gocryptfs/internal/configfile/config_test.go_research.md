# sources/security-integrity/gocryptfs/internal/configfile/config_test.go

Purpose: This test suite validates config loading, decryption, creation, feature flags, KDF behavior, and compatibility fixtures.

Important APIs and functions: It tests `LoadAndDecrypt`, `Create`, `ContentEncryption`, feature flag recognition, plaintext-name configs, AES-SIV reverse-mode configs, long-name settings, and wrong-password behavior using fixture files.

Control flow and state: Tests load static configs, create temporary config files, check generated feature flags and encrypted key behavior, and assert KDF runtime is not trivially fast.

Dependencies and integration points: Covers configfile integration with content encryption, scrypt, tlog warning control, and fixture configs in `config_test/`.

Risks and test signals: Time-based scrypt minimum checks can be environment-sensitive. Strong signals are v1 rejection, v2 successful decrypt, wrong password failure, generated feature flags, and known/unknown feature handling.
