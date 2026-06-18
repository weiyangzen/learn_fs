<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/user/hash_password.go -->
# sources/sync-backup/kopia/internal/user/hash_password.go

- Purpose: Encodes generated password hashes into a base64 JSON payload suitable for profile import/set operations.
- Important APIs/types/functions: `passwordHash`, `HashPassword`, `decodeHashedPassword`, `validate`.
- Control flow: `HashPassword` generates a random salt, computes the default-version password hash, marshals version plus hash bytes to JSON, and base64-encodes it. Decoding reverses base64/JSON. Validation checks known algorithm version and salt+hash length.
- State and persistence: No direct repository writes; encoded output can be stored into `Profile`.
- Dependencies and integration points: Uses `computePasswordHash`, default hash version, crypto random source, and JSON/base64 encoding.
- Risks and edge cases: Encoded hashes are only as strong as the selected default algorithm; validation rejects unknown versions and malformed lengths.
- Test signals: `hash_password_test.go` covers encoding round trip and validation failures/success.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/user/hash_password.go -->
