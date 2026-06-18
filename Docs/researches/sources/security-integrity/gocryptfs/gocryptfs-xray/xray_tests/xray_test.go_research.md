# sources/security-integrity/gocryptfs/gocryptfs-xray/xray_tests/xray_test.go

Purpose: This test suite validates `gocryptfs-xray` against bundled AES-GCM and AES-SIV fixture filesystems.

Important APIs and functions: Tests execute or call xray functionality to inspect configs, decrypt known data, translate names, and verify expected output for fixture directories.

Control flow and state: Tests read static fixture config/files and compare output. They should avoid mutating fixtures.

Dependencies and integration points: Covers xray main logic, configfile parsing, content/name crypto setup, and ctlsock-independent fixture inspection.

Risks and test signals: Fixture tests can become brittle when output text changes. Strong signals are exact expected fields, decrypted names, and mode-specific behavior for AES-GCM versus AES-SIV.
