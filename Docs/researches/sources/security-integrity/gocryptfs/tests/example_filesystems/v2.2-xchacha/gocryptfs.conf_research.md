# sources/security-integrity/gocryptfs/tests/example_filesystems/v2.2-xchacha/gocryptfs.conf

Purpose: Historical or intentionally broken gocryptfs JSON configuration fixture used by compatibility, fsck, or HKDF sanity tests.

Important APIs and types: JSON fixture fields: Creator=gocryptfs v2.1-27-gabaa129-dirty.xchacha, Version=2, Scrypt N=1024, FeatureFlags=['HKDF', 'XChaCha20Poly1305', 'DirIV', 'EMENames', 'LongNames', 'Raw64'].

Control flow: There is no executable flow. Compatibility and fsck tests load this fixture through gocryptfs config parsing, decrypt with the known test password or master key, and compare behavior with adjacent ciphertext fixture files. HKDF flags are compatibility-critical because content and name key derivation changes must not be silently ignored. This JSON fixture stores encrypted key metadata with Scrypt N=1024, Version=2, Creator=gocryptfs v2.1-27-gabaa129-dirty.xchacha, FeatureFlags=['HKDF', 'XChaCha20Poly1305', 'DirIV', 'EMENames', 'LongNames', 'Raw64'].

State and persistence behavior: Checked-in persistent encrypted master-key metadata and feature flags. The fixture must remain byte-compatible with the surrounding encrypted files.

Dependencies and integration points: `configfile parser`, `test password/masterkey`, `neighboring encrypted fixture files`

Risks: editing flags, salts, or encrypted key material can invalidate historical compatibility expectations.

Test signals: This file is itself a test signal; success means the described regression or compatibility behavior still holds. Assertions and subprocess exit codes in the file provide direct pass/fail evidence.
