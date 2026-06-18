<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/user/user_profile_pw_hash.go -->
# sources/sync-backup/kopia/internal/user/user_profile_pw_hash.go

- Purpose: Implements salted password hash derivation and constant-time password verification.
- Important APIs/types/functions: `dummyHashThatNeverMatchesAnyPassword`, `initDummyHash`, `setPassword`, `computePasswordHash`, `isValidPassword`.
- Control flow: Password setting generates random salt and stores salt+derived key. Hash computation maps version to algorithm, derives a fixed-length key, and prefixes salt. Validation checks payload length, recomputes with stored salt, and uses `subtle.ConstantTimeCompare`.
- State and persistence: Stores salt+hash bytes in the caller's `Profile`; dummy hash is process-global read-only state.
- Dependencies and integration points: Uses `internal/crypto` password key derivation and version mapping.
- Risks and edge cases: Unknown hash versions return errors during recomputation; invalid lengths return false without hashing.
- Test signals: Covered by user profile and hashing tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/user/user_profile_pw_hash.go -->
