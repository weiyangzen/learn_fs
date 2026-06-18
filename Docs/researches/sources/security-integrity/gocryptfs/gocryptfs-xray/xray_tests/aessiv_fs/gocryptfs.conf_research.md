# sources/security-integrity/gocryptfs/gocryptfs-xray/xray_tests/aessiv_fs/gocryptfs.conf

Purpose: This fixture config represents an AES-SIV gocryptfs filesystem for xray tests.

Important fields: It stores version/creator metadata, feature flags including AES-SIV-related behavior, scrypt KDF settings, and encrypted master key bytes.

Control flow and state: Static persistent configuration only. Tests load it to verify alternate content/name crypto paths.

Dependencies and integration points: Used by `gocryptfs-xray` tests and configfile/content encryption selection logic.

Risks and test signals: The fixture must remain aligned with known password and expected output. Signals include config parse/decrypt success and xray recognition of AES-SIV mode.
