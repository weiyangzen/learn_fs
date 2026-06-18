## sources/sync-backup/restic/internal/repository/crypto/kdf_test.go

Purpose: smoke test for scrypt parameter calibration.

Important tests: `TestCalibrate` calls `Calibrate(100*time.Millisecond, 50)` and logs the returned params.

Control flow and state: hardware-dependent output is intentionally not fixed. The test only fails if calibration returns an error.

Dependencies and integration points: validates the simple-scrypt calibration path used for repository key setup.

Risks and test signals: weak signal for KDF correctness; it does not test `KDF`, salt length errors, or deterministic derived keys. It may be sensitive to very constrained CI environments if calibration fails.
