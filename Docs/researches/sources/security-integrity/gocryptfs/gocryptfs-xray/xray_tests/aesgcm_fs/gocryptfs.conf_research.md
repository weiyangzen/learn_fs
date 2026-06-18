# sources/security-integrity/gocryptfs/gocryptfs-xray/xray_tests/aesgcm_fs/gocryptfs.conf

Purpose: This fixture config represents a small AES-GCM gocryptfs filesystem used by xray tests.

Important fields: It contains creator/version metadata, feature flags such as HKDF/GCM IV/name encryption settings, scrypt parameters, and encrypted master key data.

Control flow and state: It is static JSON-like persistent filesystem configuration. Tests read and decrypt it with known credentials.

Dependencies and integration points: Used by `xray_test.go` and configfile loading/decryption code to verify AES-GCM fixture behavior.

Risks and test signals: Fixture drift can break expected vectors. Signals are successful config parse, expected feature flags, and reproducible xray output.
