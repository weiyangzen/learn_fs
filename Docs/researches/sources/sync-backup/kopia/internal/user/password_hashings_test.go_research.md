<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/user/password_hashings_test.go -->
# sources/sync-backup/kopia/internal/user/password_hashings_test.go

- Purpose: Guards password hashing constants and salt/dummy hash invariants.
- Important APIs/types/functions: `TestPasswordHashingConstantMatchCryptoPackage`, `TestNonZeroDummyHash`, `TestSaltLengthIsSupported`.
- Control flow: Compares package algorithm strings to crypto package constants, checks dummy hash is non-zero, and derives hashes with both supported versions using the configured salt length.
- State and persistence: In-memory constants and derived hashes only.
- Dependencies and integration points: Integrates `internal/crypto`.
- Risks and edge cases: Does not benchmark algorithm cost; it is a compatibility and invariant test.
- Test signals: Direct coverage for version/algorithm mapping assumptions.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/user/password_hashings_test.go -->
